import clsx from 'clsx';

const styles: Record<string, string> = {
  success: 'bg-emerald-100 text-emerald-700',
  manual_review: 'bg-amber-100 text-amber-700',
  no_fit: 'bg-rose-100 text-rose-700',
  split_recommendation: 'bg-indigo-100 text-indigo-700',
};

export function StatusBadge({ value }: { value?: string | null }) {
  const key = value ?? 'unknown';
  return <span className={clsx('rounded-full px-2 py-1 text-xs font-semibold', styles[key] ?? 'bg-slate-100 text-slate-700')}>{key}</span>;
}
