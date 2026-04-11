import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../app/auth-context';

export function LoginPage() {
  const demoUsers = [
    { role: 'Admin', email: 'admin@logitracks.local', password: 'admin123' },
    { role: 'Planner', email: 'planner@logitracks.local', password: 'planner123' },
    { role: 'Analyst', email: 'analyst@logitracks.local', password: 'analyst123' },
  ];
  const [email, setEmail] = useState(demoUsers[0].email);
  const [password, setPassword] = useState(demoUsers[0].password);
  const [error, setError] = useState<string>('');
  const [busy, setBusy] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation() as { state?: { from?: string } };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError('');
    try {
      await login({ email, password });
      navigate(location.state?.from ?? '/dashboard', { replace: true });
    } catch {
      setError('Login failed. Verify credentials or backend connectivity.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <form onSubmit={onSubmit} className="mx-auto mt-20 max-w-md rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
      <h2 className="text-2xl font-semibold">LogiTracks Login</h2>
      <p className="mt-2 text-sm text-slate-500">Use seeded demo accounts to sign in.</p>
      <div className="mt-4 rounded-md border border-amber-200 bg-amber-50 p-3 text-xs text-slate-700">
        <p className="font-semibold text-slate-800">Demo credentials</p>
        <ul className="mt-2 space-y-1">{demoUsers.map((user) => <li key={user.email}><span className="font-medium">{user.role}:</span> {user.email} / {user.password}</li>)}</ul>
      </div>
      <div className="mt-6 space-y-3">
        <input className="w-full rounded border border-slate-300 px-3 py-2" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input className="w-full rounded border border-slate-300 px-3 py-2" placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        {error ? <p className="text-sm text-rose-600">{error}</p> : null}
        <button className="w-full rounded bg-brand-600 px-3 py-2 text-white" disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</button>
      </div>
    </form>
  );
}
