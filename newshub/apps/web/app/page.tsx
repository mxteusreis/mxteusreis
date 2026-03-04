import Link from 'next/link';

export default function HomePage() {
  return (
    <section className='space-y-4'>
      <h1 className='text-3xl font-bold'>Seu hub de notícias personalizado</h1>
      <p className='text-slate-600'>Acompanhe somente as fontes que importam para você.</p>
      <Link href='/login' className='inline-block rounded-md bg-slate-900 px-4 py-2 text-white'>
        Entrar
      </Link>
    </section>
  );
}
