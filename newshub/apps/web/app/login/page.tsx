'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import { UIButton } from '@/components/ui-button';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function handleLogin() {
    setLoading(true);
    await supabase.auth.signInWithOtp({ email });
    setLoading(false);
    router.push('/onboarding');
  }

  return (
    <section className='mx-auto max-w-md space-y-3'>
      <h1 className='text-2xl font-semibold'>Login</h1>
      <input
        className='w-full rounded-md border px-3 py-2'
        placeholder='voce@email.com'
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <UIButton onClick={handleLogin} disabled={loading || !email}>
        {loading ? 'Enviando...' : 'Receber magic link'}
      </UIButton>
    </section>
  );
}
