import { Link } from 'react-router-dom';
import { DataTable } from '../components/DataTable';
import { useOrders } from '../hooks/useApi';
import type { OrderListItem } from '../types/domain';
import { QueryBlock } from './shared';

export function OrderListPage() {
  const { data, isLoading, isError } = useOrders();
  const orders: OrderListItem[] = data ?? [];

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Order List</h2>
      <QueryBlock isLoading={isLoading} isError={isError} isEmpty={!orders.length}>
        <DataTable<OrderListItem>
          data={orders}
          columns={[
            {
              key: 'order',
              header: 'Order',
              render: (r) => (
                <Link className="text-brand-700 underline" to={`/orders/${r.order_id}`}>
                  {r.order_no ?? `#${r.order_id}`}
                </Link>
              ),
            },
            { key: 'customer', header: 'Customer', render: (r) => r.customer_name ?? '-' },
            { key: 'date', header: 'Planned Date', render: (r) => r.planned_delivery_date ?? '-' },
            { key: 'weight', header: 'Total Weight', render: (r) => r.total_weight_kg ?? '-' },
            { key: 'volume', header: 'Total Volume', render: (r) => r.total_volume_m3 ?? '-' },
          ]}
        />
      </QueryBlock>
    </div>
  );
}
