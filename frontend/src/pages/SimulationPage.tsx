import { useParams } from 'react-router-dom';
import { DataTable } from '../components/DataTable';
import { StatusBadge } from '../components/StatusBadge';
import { useSimulation } from '../hooks/useApi';
import { QueryBlock } from './shared';

export function SimulationPage() {
  const { runId } = useParams();
  const { data, isLoading, isError } = useSimulation(runId);
  return <QueryBlock isLoading={isLoading} isError={isError} isEmpty={!data}><div className="space-y-4"><h2 className="text-2xl font-semibold">Simulation / Run Detail</h2>
    <div className="rounded-lg border border-slate-200 bg-white p-4 text-sm">Run #{data!.run_id} · Order #{data!.order_id} · <StatusBadge value={data!.recommendation_status}/> · {data!.recommendation_reason ?? '-'}</div>
    <DataTable data={data!.run_items} columns={[{key:'sku',header:'Run Items',render:(r:any)=>`${r.sku_code ?? '-'} / ${r.product_name ?? '-'}`},{key:'qty',header:'Qty',render:(r:any)=>r.qty_shipping_pack ?? '-'},{key:'weight',header:'Weight',render:(r:any)=>r.total_weight_kg ?? '-'},{key:'volume',header:'Volume',render:(r:any)=>r.total_volume_m3 ?? '-'},{key:'stack',header:'Stack Layers',render:(r:any)=>`${r.stack_layers_used ?? '-'} / ${r.max_stack_layer ?? '-'}`},]} />
    <DataTable data={data!.candidates} columns={[{key:'truck',header:'Truck Name',render:(r:any)=>r.truck_name ?? '-'},{key:'payload',header:'Payload (kg)',render:(r:any)=>r.max_payload_kg ?? '-'},{key:'volume',header:'Volume (m3)',render:(r:any)=>r.cargo_volume_m3 ?? '-'},{key:'util',header:'Utilization %',render:(r:any)=>`W ${r.weight_utilization_pct ?? '-'} | V ${r.volume_utilization_pct ?? '-'}`},{key:'pass',header:'Pass/Fail',render:(r:any)=>`W:${r.pass_weight?'✓':'✗'} V:${r.pass_volume?'✓':'✗'} F:${r.pass_floor_area?'✓':'✗'} H:${r.pass_height?'✓':'✗'}`},{key:'rank',header:'Rank',render:(r:any)=>r.rank_no ?? '-'},{key:'reason',header:'Rejection Reason',render:(r:any)=>r.rejection_reason ?? '-'}]} />
    {data!.split_recommendation?.length ? <div className="rounded-lg border border-indigo-200 bg-indigo-50 p-3 text-sm"><b>Split recommendation</b>: {data!.split_recommendation.join(', ')}</div> : null}
  </div></QueryBlock>;
}
