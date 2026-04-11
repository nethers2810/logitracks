import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { DataTable } from '../components/DataTable';
import { SummaryCard } from '../components/SummaryCard';
import { useOrderDetail } from '../hooks/useApi';
import { api } from '../lib/api';
import { QueryBlock } from './shared';

export function OrderDetailPage() {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const { data, isLoading, isError, refetch } = useOrderDetail(orderId);
  const [running, setRunning] = useState(false);

  const runSimulation = async () => {
    if (!orderId) return;
    setRunning(true);
    try {
      const res = await api.post(`/orders/${orderId}/simulate`);
      await refetch();
      navigate(`/simulation/${res.data.run_id}`);
    } finally {
      setRunning(false);
    }
  };

  return <QueryBlock isLoading={isLoading} isError={isError} isEmpty={!data}><div className="space-y-4">
    <div className="flex items-center justify-between"><h2 className="text-2xl font-semibold">Order Detail</h2><div className="flex gap-2">
      {data!.latest_run_id ? <Link className="rounded border border-brand-600 px-3 py-2 text-sm text-brand-700" to={`/simulation/${data!.latest_run_id}`}>View latest run</Link> : null}
      <button className="rounded bg-brand-600 px-3 py-2 text-sm text-white" onClick={runSimulation} disabled={running}>{running ? 'Running...' : 'Run Smart Cubication'}</button>
    </div></div>
    <div className="rounded-lg border border-slate-200 bg-white p-4 text-sm">Order: {data!.header.order_no} · Customer: {data!.header.customer_name} · Status: {data!.header.status}</div>
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      <SummaryCard title="Items" value={data!.summary.item_count} />
      <SummaryCard title="Total Weight (kg)" value={data!.summary.total_weight_kg.toFixed(2)} />
      <SummaryCard title="Total Volume (m3)" value={data!.summary.total_volume_m3.toFixed(2)} />
    </div>
    <DataTable data={data!.items} columns={[{key:'line',header:'Line',render:(r:any)=>r.line_no},{key:'sku',header:'Product',render:(r:any)=>`${r.sku_code ?? '-'} / ${r.product_name ?? '-'}`},{key:'sap',header:'SAP Shipping Qty',render:(r:any)=>`${r.sap_shipping_qty ?? '-'} ${r.qty_uom ?? ''}`},{key:'base',header:'Base Qty',render:(r:any)=>r.base_qty ?? '-'},{key:'stack',header:'Stacking Info',render:(r:any)=>`${r.stacking_rule_code ?? '-'} (max ${r.max_stack_layer ?? '-'})`},{key:'weight',header:'Weight/Volume',render:(r:any)=>`${r.gross_weight_total_kg ?? '-'} kg / ${r.volume_total_m3 ?? '-'} m3`}]} />
  </div></QueryBlock>;
}
