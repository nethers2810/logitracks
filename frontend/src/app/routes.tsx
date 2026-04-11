import type { ReactElement } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { AppLayout } from '../layout/AppLayout';
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';
import { ProductPage } from '../pages/ProductPage';
import { TruckTypePage } from '../pages/TruckTypePage';
import { StackingRulePage } from '../pages/StackingRulePage';
import { CustomerPage } from '../pages/CustomerPage';
import { VendorAllocationPage } from '../pages/VendorAllocationPage';
import { OrderListPage } from '../pages/OrderListPage';
import { OrderDetailPage } from '../pages/OrderDetailPage';
import { SimulationPage } from '../pages/SimulationPage';
import { ImportCenterPage } from '../pages/ImportCenterPage';
import { authStore } from '../lib/api';

function Protected({ children }: { children: ReactElement }) {
  return authStore.getToken() ? children : <Navigate to="/login" replace />;
}

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<Protected><AppLayout /></Protected>}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/products" element={<ProductPage />} />
        <Route path="/truck-types" element={<TruckTypePage />} />
        <Route path="/stacking-rules" element={<StackingRulePage />} />
        <Route path="/customers" element={<CustomerPage />} />
        <Route path="/vendor-allocation" element={<VendorAllocationPage />} />
        <Route path="/orders" element={<OrderListPage />} />
        <Route path="/orders/:orderId" element={<OrderDetailPage />} />
        <Route path="/simulation/:runId" element={<SimulationPage />} />
        <Route path="/imports" element={<ImportCenterPage />} />
      </Route>
    </Routes>
  );
}
