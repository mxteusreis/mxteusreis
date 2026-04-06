import sys
import types
import unittest
from unittest.mock import Mock, patch

import httpx

if 'feedparser' not in sys.modules:
    fake_feedparser = types.ModuleType('feedparser')
    fake_feedparser.parse = lambda _text: types.SimpleNamespace(entries=[])
    sys.modules['feedparser'] = fake_feedparser

if 'supabase' not in sys.modules:
    fake_supabase = types.ModuleType('supabase')
    fake_supabase.Client = object
    fake_supabase.create_client = lambda *_args, **_kwargs: None
    sys.modules['supabase'] = fake_supabase

if 'app.services.db' not in sys.modules:
    fake_db = types.ModuleType('app.services.db')
    fake_db.get_service_client = lambda: None
    sys.modules['app.services.db'] = fake_db

from app.services.ingest import ensure_url_has_scheme, ingest_rss_sources


class FakeQuery:
    def __init__(self, data=None):
        self._data = data or []
        self._eq_filters = {}

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, *_args, **_kwargs):
        if len(_args) >= 2:
            self._eq_filters[_args[0]] = _args[1]
        return self

    def limit(self, *_args, **_kwargs):
        return self

    def insert(self, *_args, **_kwargs):
        return self

    def execute(self):
        return type('Resp', (), {'data': self._data})()


class FakeClient:
    def __init__(self, sources, existing_urls=None, existing_hashes=None):
        self.sources = sources
        self.existing_urls = set(existing_urls or [])
        self.existing_hashes = set(existing_hashes or [])
        self.inserted = []

    def table(self, name):
        if name == 'sources':
            return FakeQuery(self.sources)
        if name == 'articles':
            query = FakeQuery([])

            def _select(*_args, **_kwargs):
                return query

            def _eq(column, value):
                query._eq_filters[column] = value
                if column == 'url':
                    query._data = [{'id': 'existing'}] if value in self.existing_urls else []
                elif column == 'hash':
                    query._data = [{'id': 'existing'}] if value in self.existing_hashes else []
                return query

            def _insert(payload):
                if payload['url'] in self.existing_urls:
                    raise Exception('duplicate key value violates unique constraint \"articles_url_key\"')
                self.existing_urls.add(payload['url'])
                self.existing_hashes.add(payload['hash'])
                self.inserted.append(payload)
                return FakeQuery([])

            query.select = _select
            query.eq = _eq
            query.insert = _insert
            return query
        raise AssertionError(f'Unexpected table: {name}')


class IngestTests(unittest.TestCase):
    def test_ensure_url_has_scheme(self):
        self.assertEqual(ensure_url_has_scheme('example.com/rss.xml'), 'https://example.com/rss.xml')
        self.assertEqual(ensure_url_has_scheme('http://example.com/rss.xml'), 'http://example.com/rss.xml')
        self.assertIsNone(ensure_url_has_scheme('ftp://example.com/rss.xml'))
        self.assertIsNone(ensure_url_has_scheme(''))

    @patch('app.services.ingest.feedparser.parse')
    @patch('app.services.ingest.httpx.get')
    @patch('app.services.ingest.get_service_client')
    def test_ingest_valid_source(self, mock_client_factory, mock_http_get, mock_parse):
        source = {'id': 's1', 'name': 'Valid', 'rss_url': 'https://example.com/rss', 'is_active': True}
        client = FakeClient([source])
        mock_client_factory.return_value = client
        mock_http_get.return_value = Mock(text='<rss/>', raise_for_status=Mock())
        entry = type('Entry', (), {'title': 'Title', 'link': 'https://news/item', 'summary': 'Resumo'})()
        mock_parse.return_value = type('Parsed', (), {'entries': [entry]})()

        result = ingest_rss_sources()

        self.assertEqual(result['sources_failed'], 0)
        self.assertEqual(result['inserted'], 1)
        self.assertEqual(len(client.inserted), 1)

    @patch('app.services.ingest.get_service_client')
    def test_ingest_invalid_source_url(self, mock_client_factory):
        source = {'id': 's1', 'name': 'Bad URL', 'rss_url': 'ftp://invalid-host', 'is_active': True}
        client = FakeClient([source])
        mock_client_factory.return_value = client

        result = ingest_rss_sources()

        self.assertEqual(result['inserted'], 0)
        self.assertEqual(result['sources_failed'], 1)
        self.assertEqual(len(result['failures']), 1)

    @patch('app.services.ingest.httpx.get')
    @patch('app.services.ingest.get_service_client')
    def test_ingest_connect_error(self, mock_client_factory, mock_http_get):
        source = {'id': 's1', 'name': 'Offline', 'rss_url': 'https://offline.example/rss', 'is_active': True}
        client = FakeClient([source])
        mock_client_factory.return_value = client
        mock_http_get.side_effect = httpx.ConnectError('getaddrinfo failed')

        result = ingest_rss_sources()

        self.assertEqual(result['inserted'], 0)
        self.assertEqual(result['sources_failed'], 1)
        self.assertIn('ConnectError', result['failures'][0]['error'])

    @patch('app.services.ingest.httpx.get')
    @patch('app.services.ingest.get_service_client')
    def test_ingest_partial_success(self, mock_client_factory, mock_http_get):
        sources = [
            {'id': 's1', 'name': 'Bad URL', 'rss_url': 'not-a-url', 'is_active': True},
            {'id': 's2', 'name': 'Offline', 'rss_url': 'https://offline.example/rss', 'is_active': True},
        ]
        client = FakeClient(sources)
        mock_client_factory.return_value = client
        mock_http_get.side_effect = httpx.ConnectError('getaddrinfo failed')

        result = ingest_rss_sources()

        self.assertEqual(result['sources_processed'], 2)
        self.assertEqual(result['sources_failed'], 2)
        self.assertEqual(result['inserted'], 0)
        self.assertEqual(len(result['failures']), 2)

    @patch('app.services.ingest.feedparser.parse')
    @patch('app.services.ingest.httpx.get')
    @patch('app.services.ingest.get_service_client')
    def test_ingest_duplicate_url_is_skipped(self, mock_client_factory, mock_http_get, mock_parse):
        source = {'id': 's1', 'name': 'Valid', 'rss_url': 'https://example.com/rss', 'is_active': True}
        client = FakeClient([source], existing_urls={'https://news/item'})
        mock_client_factory.return_value = client
        mock_http_get.return_value = Mock(text='<rss/>', raise_for_status=Mock())
        entry = type('Entry', (), {'title': 'Title 2', 'link': 'https://news/item', 'summary': 'Resumo'})()
        mock_parse.return_value = type('Parsed', (), {'entries': [entry]})()

        result = ingest_rss_sources()

        self.assertEqual(result['inserted'], 0)
        self.assertEqual(result['skipped'], 1)

if __name__ == '__main__':
    unittest.main()
