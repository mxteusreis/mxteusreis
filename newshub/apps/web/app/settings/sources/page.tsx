'use client';

import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import { UIButton } from '@/components/ui-button';

type Row = {
  source_id: string;
  sources: { id: string; name: string; category: string };
};

type Source = { id: string; name: string; category: string };

export default function SettingsSourcesPage() {
  const [allSources, setAllSources] = useState<Source[]>([]);
  const [selected, setSelected] = useState<string[]>([]);

  useEffect(() => {
    async function load() {
      const { data } = await supabase.auth.getSession();
      const token = data.session?.access_token;

      const [sourcesRes, prefsRes] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/sources`),
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/preferences/sources`, { headers: { Authorization: `Bearer ${token}` } }),
      ]);

      const sourcesData = (await sourcesRes.json()) as Source[];
      const prefData = (await prefsRes.json()) as Row[];

      setAllSources(sourcesData);
      setSelected(prefData.map((item) => item.source_id));
    }

    load();
  }, []);

  function toggle(id: string) {
    setSelected((prev) => (prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]));
  }

  async function save() {
    const { data } = await supabase.auth.getSession();
    const token = data.session?.access_token;
    await fetch(`${process.env.NEXT_PUBLIC_API_URL}/preferences/sources`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ source_ids: selected }),
    });
  }

  return (
    <section className='space-y-4'>
      <h1 className='text-2xl font-semibold'>Fontes selecionadas</h1>
      <div className='grid gap-2 sm:grid-cols-2'>
        {allSources.map((source) => (
          <label key={source.id} className='flex items-center gap-2 rounded border bg-white p-3'>
            <input type='checkbox' checked={selected.includes(source.id)} onChange={() => toggle(source.id)} />
            <span>
              {source.name} <small className='text-slate-500'>({source.category})</small>
            </span>
          </label>
        ))}
      </div>
      <UIButton onClick={save}>Salvar preferências</UIButton>
    </section>
  );
}
