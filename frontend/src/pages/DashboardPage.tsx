import { DataTable } from '../components/DataTable';
import { StatusBadge } from '../components/StatusBadge';
import { SummaryCard } from '../components/SummaryCard';
import { useDashboard } from '../hooks/useApi';
import { QueryBlock } from './shared';

export function DashboardPage() {
  const { data, isLoading, isError } = useDashboard() as any;
  return <QueryBlock isLoading={isLoading} isError={isError} isEmpty={!data}>{
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Dashboard</h2>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        <SummaryCard title="Products" value={data.summary.products} />
        <SummaryCard title="Orders" value={data.summary.orders} />
        <SummaryCard title="Runs" value={data.summary.runs} />
        <SummaryCard title="Imports" value={data.summary.imports} />
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <DataTable data={data.recentImports} columns={[{key:'file',header:'Recent Imports',render:(r:any)=>r.file_name},{key:'status',header:'Status',render:(r:any)=><StatusBadge value={r.status}/>},{key:'rows',header:'Rows',render:(r:any)=>r.row_count}]} />
        <DataTable data={data.recentRuns} columns={[{key:'run',header:'Recent Runs',render:(r:any)=>`Run #${r.run_id}`},{key:'status',header:'Result',render:(r:any)=><StatusBadge value={r.recommendation_status}/>},{key:'order',header:'Order',render:(r:any)=>r.order_no ?? '-'}]} />
      </div>
      <DataTable data={data.recommendationBreakdown} columns={[{key:'status',header:'Recommendation Breakdown',render:(r:any)=><StatusBadge value={r.recommendation_status}/>},{key:'count',header:'Count',render:(r:any)=>r.count}]} />
    </div>
  }</QueryBlock>;
}
