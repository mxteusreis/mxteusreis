'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { UIButton } from '@/components/ui-button';
import { supabase } from '@/lib/supabase';

type Source = { id: string; name: string; category: string };

export default function OnboardingPage() {
  const [sources, setSources] = useState<Source[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const router = useRouter();

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/sources`)
      .then((res) => res.json())
      .then(setSources);
  }, []);

  const grouped = useMemo(() => {
    return sources.reduce<Record<string, Source[]>>((acc, source) => {
      acc[source.category] = acc[source.category] || [];
      acc[source.category].push(source);
      return acc;
    }, {});
  }, [sources]);

  function toggle(id: string) {
    setSelected((prev) => (prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]));
  }

  async function savePreferences() {
    const { data } = await supabase.auth.getSession();
    const token = data.session?.access_token;
    await fetch(`${process.env.NEXT_PUBLIC_API_URL}/preferences/sources`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ source_ids: selected }),
    });
    router.push('/app');
  }

  return (
    <section className='space-y-6'>
      <h1 className='text-2xl font-semibold'>Escolha suas fontes</h1>
      {Object.entries(grouped).map(([category, items]) => (
        <div key={category}>
          <h2 className='mb-2 text-lg font-medium'>{category}</h2>
          <div className='grid gap-2 sm:grid-cols-2'>
            {items.map((source) => (
              <label key={source.id} className='flex items-center gap-2 rounded border bg-white p-3'>
                <input type='checkbox' checked={selected.includes(source.id)} onChange={() => toggle(source.id)} />
                <span>{source.name}</span>
              </label>
            ))}
          </div>
        </div>
      ))}
      <UIButton onClick={savePreferences}>Continuar</UIButton>
    </section>
  );
}
