import './globals.css';
import Link from 'next/link';
import { ReactNode } from 'react';

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang='pt-BR'>
      <body>
        <header className='border-b bg-white'>
          <div className='mx-auto flex max-w-5xl items-center justify-between px-4 py-3'>
            <Link href='/' className='font-semibold'>
              newshub
            </Link>
            <nav className='space-x-4 text-sm'>
              <Link href='/app'>Feed</Link>
              <Link href='/settings/sources'>Fontes</Link>
            </nav>
          </div>
        </header>
        <main className='mx-auto max-w-5xl px-4 py-6'>{children}</main>
      </body>
    </html>
  );
}
