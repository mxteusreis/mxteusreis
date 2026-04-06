'use client';

import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';

type Article = {
  id: string;
  title: string;
  url: string;
  excerpt: string;
  image_url?: string;
  published_at: string;
  sources: { name: string; category: string };
};

export default function FeedPage() {
  const [articles, setArticles] = useState<Article[]>([]);

  useEffect(() => {
    async function loadFeed() {
      const { data } = await supabase.auth.getSession();
      const token = data.session?.access_token;
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/feed?limit=30&offset=0`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const payload = await res.json();
      setArticles(payload);
    }
    loadFeed();
  }, []);

  return (
    <section className='space-y-4'>
      <h1 className='text-2xl font-semibold'>Seu feed</h1>
      {articles.map((article) => (
        <article key={article.id} className='rounded-lg border bg-white p-4'>
          <p className='text-xs text-slate-500'>
            {article.sources?.name} · {new Date(article.published_at).toLocaleString('pt-BR')}
          </p>
          <h2 className='text-lg font-semibold'>{article.title}</h2>
          <p className='text-sm text-slate-600'>{article.excerpt}</p>
          <a className='text-sm text-blue-600 hover:underline' href={article.url} target='_blank'>
            Ler na fonte original
          </a>
        </article>
      ))}
    </section>
  );
}
