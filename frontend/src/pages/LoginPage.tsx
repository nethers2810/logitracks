export function LoginPage() {
  const demoUsers = [
    { role: 'Admin', email: 'admin@logitracks.local', password: 'admin123' },
    { role: 'Planner', email: 'planner@logitracks.local', password: 'planner123' },
    { role: 'Analyst', email: 'analyst@logitracks.local', password: 'analyst123' },
  ];

  return (
    <div className="mx-auto mt-20 max-w-md rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
      <h2 className="text-2xl font-semibold">LogiTracks Login</h2>
      <p className="mt-2 text-sm text-slate-500">
        Use a seeded Stage 6 demo account (email + password) to sign in via the backend auth API.
      </p>
      <div className="mt-4 rounded-md border border-amber-200 bg-amber-50 p-3 text-xs text-slate-700">
        <p className="font-semibold text-slate-800">Demo credentials</p>
        <ul className="mt-2 space-y-1">
          {demoUsers.map((user) => (
            <li key={user.email}>
              <span className="font-medium">{user.role}:</span> {user.email} / {user.password}
            </li>
          ))}
        </ul>
      </div>
      <div className="mt-6 space-y-3">
        <input className="w-full rounded border border-slate-300 px-3 py-2" placeholder="Email" disabled />
        <input className="w-full rounded border border-slate-300 px-3 py-2" placeholder="Password" type="password" disabled />
        <button className="w-full rounded bg-brand-600 px-3 py-2 text-white" disabled>Sign in (disabled)</button>
      </div>
    </div>
  );
}
