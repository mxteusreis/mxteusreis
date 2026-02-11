from unittest.mock import Mock, patch

from producer.binance_client import fetch_ticker_24h


@patch("producer.binance_client.requests.get")
def test_fetch_ticker_24h_returns_list(mock_get: Mock) -> None:
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = [
        {
            "symbol": "BTCUSDT",
            "lastPrice": "65000.00",
            "priceChangePercent": "2.10",
            "volume": "12345.67",
        }
    ]
    mock_get.return_value = mock_response

    result = fetch_ticker_24h(["BTCUSDT"])

    assert isinstance(result, list)
    assert len(result) == 1


@patch("producer.binance_client.requests.get")
def test_fetch_ticker_24h_event_contract(mock_get: Mock) -> None:
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = [
        {
            "symbol": "ETHUSDT",
            "lastPrice": "3500.12",
            "priceChangePercent": "-1.11",
            "volume": "9988.77",
        }
    ]
    mock_get.return_value = mock_response

    result = fetch_ticker_24h(["ETHUSDT"])

    event = result[0]
    expected_keys = {
        "timestamp_utc",
        "symbol",
        "lastPrice",
        "priceChangePercent",
        "volume",
        "source",
    }

    assert expected_keys.issubset(set(event.keys()))
    assert event["symbol"] == "ETHUSDT"
