import { Link } from 'react-router-dom';
import { DataTable } from '../components/DataTable';
import { useOrders } from '../hooks/useApi';
import { QueryBlock } from './shared';

export function OrderListPage() {
  const { data, isLoading, isError } = useOrders();
  return <div className="space-y-4"><h2 className="text-2xl font-semibold">Order List</h2><QueryBlock isLoading={isLoading} isError={isError} isEmpty={!data?.length}><DataTable data={data} columns={[{key:'order',header:'Order',render:(r:any)=><Link className="text-brand-700 underline" to={`/orders/${r.order_id}`}>{r.order_no ?? `#${r.order_id}`}</Link>},{key:'customer',header:'Customer',render:(r:any)=>r.customer_name ?? '-'},{key:'date',header:'Planned Date',render:(r:any)=>r.planned_delivery_date ?? '-'},{key:'weight',header:'Total Weight',render:(r:any)=>r.total_weight_kg ?? '-'},{key:'volume',header:'Total Volume',render:(r:any)=>r.total_volume_m3 ?? '-'}]} /></QueryBlock></div>;
}
