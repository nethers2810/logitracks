import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import type { Customer, ImportLog, OrderDetail, OrderListItem, Product, SimulationDetail, StackingRule, TruckType, ValidationError, VendorAllocation } from '../types/domain';

const get = async <T,>(path: string) => (await api.get<T>(path)).data;

export const useDashboard = () => useQuery({ queryKey: ['dashboard'], queryFn: () => get('/dashboard') });
export const useProducts = () => useQuery({ queryKey: ['products'], queryFn: () => get<Product[]>('/products') });
export const useTruckTypes = () => useQuery({ queryKey: ['truck-types'], queryFn: () => get<TruckType[]>('/truck-types') });
export const useStackingRules = () => useQuery({ queryKey: ['stacking-rules'], queryFn: () => get<StackingRule[]>('/stacking-rules') });
export const useCustomers = () => useQuery({ queryKey: ['customers'], queryFn: () => get<Customer[]>('/customers') });
export const useVendorAllocations = () => useQuery({ queryKey: ['vendor-allocations'], queryFn: () => get<VendorAllocation[]>('/vendor-allocations') });
export const useOrders = () => useQuery({ queryKey: ['orders'], queryFn: () => get<OrderListItem[]>('/orders') });
export const useOrderDetail = (orderId?: string) => useQuery({ queryKey: ['order', orderId], queryFn: () => get<OrderDetail>(`/orders/${orderId}`), enabled: !!orderId });
export const useSimulation = (runId?: string) => useQuery({ queryKey: ['simulation', runId], queryFn: () => get<SimulationDetail>(`/simulation-runs/${runId}`), enabled: !!runId });
export const useImportLogs = () => useQuery({ queryKey: ['imports-logs'], queryFn: () => get<ImportLog[]>('/imports/logs') });
export const useValidationErrors = (logId?: number) => useQuery({ queryKey: ['validation-errors', logId], queryFn: () => get<ValidationError[]>(`/imports/logs/${logId}/errors`), enabled: !!logId });
