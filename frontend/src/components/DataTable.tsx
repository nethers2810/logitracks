import { ReactNode } from 'react';

interface Column<T> { key: string; header: string; render: (row: T) => ReactNode; }

export function DataTable<T>({ data, columns }: { data: T[]; columns: Column<T>[] }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
      <table className="min-w-full">
        <thead className="bg-slate-50">
          <tr>{columns.map((c) => <th key={c.key} className="table-cell text-left text-xs uppercase text-slate-500">{c.header}</th>)}</tr>
        </thead>
        <tbody>{data.map((row, idx) => <tr key={idx} className="hover:bg-slate-50">{columns.map((c) => <td key={c.key} className="table-cell">{c.render(row)}</td>)}</tr>)}</tbody>
      </table>
    </div>
  );
}
