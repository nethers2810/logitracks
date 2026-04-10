import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { api } from '../lib/api';
import { useImportLogs, useValidationErrors } from '../hooks/useApi';
import { DataTable } from '../components/DataTable';
import { QueryBlock } from './shared';

const schema = z.object({ file: z.any().refine((v) => v?.[0], 'File is required') });
const importTargets = [
  ['Products', '/imports/products'], ['Customers', '/imports/customers'], ['Trucks', '/imports/trucks'], ['Vendor Allocation', '/imports/vendor-allocation'], ['SAP Deliveries', '/imports/sap-deliveries']
];

function UploadCard({ label, endpoint }: { label:string; endpoint:string }) {
  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<{ file: FileList }>({ resolver: zodResolver(schema) });
  const [message, setMessage] = useState<string>('');
  const onSubmit = async (values: { file: FileList }) => {
    const form = new FormData();
    form.append('file', values.file[0]);
    await api.post(endpoint, form);
    setMessage('Uploaded successfully');
    reset();
  };
  return <form onSubmit={handleSubmit(onSubmit)} className="rounded-lg border border-slate-200 bg-white p-4"><div className="font-medium">{label}</div><input className="mt-2 block w-full text-sm" type="file" {...register('file')} />{errors.file ? <p className="text-xs text-rose-600">{errors.file.message as string}</p> : null}<button className="mt-3 rounded bg-brand-600 px-3 py-1 text-sm text-white" disabled={isSubmitting}>Upload</button>{message ? <p className="mt-2 text-xs text-emerald-700">{message}</p> : null}</form>;
}

export function ImportCenterPage() {
  const [selectedLog, setSelectedLog] = useState<number>();
  const logs = useImportLogs();
  const errors = useValidationErrors(selectedLog);

  return <div className="space-y-5"><h2 className="text-2xl font-semibold">Import Center</h2>
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">{importTargets.map(([label, endpoint]) => <UploadCard key={endpoint} label={label} endpoint={endpoint} />)}</div>
    <QueryBlock isLoading={logs.isLoading} isError={logs.isError} isEmpty={!logs.data?.length}><DataTable data={logs.data!} columns={[{key:'id',header:'Import Logs',render:(r:any)=>r.import_log_id},{key:'source',header:'Source',render:(r:any)=>r.source_name ?? '-'},{key:'file',header:'File',render:(r:any)=>r.file_name ?? '-'},{key:'status',header:'Status',render:(r:any)=>r.status ?? '-'},{key:'errors',header:'Errors',render:(r:any)=><button className="text-brand-700 underline" onClick={() => setSelectedLog(r.import_log_id)}>{r.error_count ?? 0}</button>}]} /></QueryBlock>
    {selectedLog ? <div className="rounded-lg border border-slate-300 bg-white p-4"><div className="mb-3 flex items-center justify-between"><h3 className="font-semibold">Validation Errors (Log {selectedLog})</h3><button onClick={() => setSelectedLog(undefined)} className="text-sm text-slate-500">Close</button></div><QueryBlock isLoading={errors.isLoading} isError={errors.isError} isEmpty={!errors.data?.length}><DataTable data={errors.data!} columns={[{key:'row',header:'Row',render:(r:any)=>r.row_identifier ?? '-'},{key:'field',header:'Field',render:(r:any)=>r.field_name ?? '-'},{key:'code',header:'Code',render:(r:any)=>r.error_code ?? '-'},{key:'msg',header:'Message',render:(r:any)=>r.error_message ?? '-'}]} /></QueryBlock></div> : null}
  </div>;
}
