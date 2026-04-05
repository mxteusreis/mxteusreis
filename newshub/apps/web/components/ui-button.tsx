import { ButtonHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

export function UIButton({ className, ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={cn('rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50', className)}
      {...props}
    />
  );
}
