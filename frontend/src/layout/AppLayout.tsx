import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { authStore } from '../lib/api';

const links = [
  ['Dashboard', '/dashboard'],
  ['Products', '/products'],
  ['Truck Types', '/truck-types'],
  ['Stacking Rules', '/stacking-rules'],
  ['Customers', '/customers'],
  ['Vendor Allocation', '/vendor-allocation'],
  ['Orders', '/orders'],
  ['Import Center', '/imports'],
];

export function AppLayout() {
  const navigate = useNavigate();
  const user = authStore.getUser();

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 border-r border-slate-200 bg-white p-4">
        <h1 className="text-lg font-semibold">Smart Cubication Pilot</h1>
        <p className="mt-1 text-xs text-slate-500">{user?.email} ({user?.role})</p>
        <button
          className="mt-3 rounded border border-slate-300 px-2 py-1 text-xs"
          onClick={() => {
            authStore.clear();
            navigate('/login', { replace: true });
          }}
        >
          Sign out
        </button>
        <nav className="mt-4 space-y-1">
          {links.map(([label, path]) => (
            <NavLink key={path} to={path} className={({ isActive }) => `block rounded px-3 py-2 text-sm ${isActive ? 'bg-brand-600 text-white' : 'text-slate-700 hover:bg-slate-100'}`}>
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="flex-1 p-6"><Outlet /></main>
    </div>
  );
}
