export function LoginPage() {
  return (
    <div className="mx-auto mt-20 max-w-md rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
      <h2 className="text-2xl font-semibold">LogiTracks Login</h2>
      <p className="mt-2 text-sm text-slate-500">Authentication is not enabled in Stage 5. This is a UI placeholder.</p>
      <div className="mt-6 space-y-3">
        <input className="w-full rounded border border-slate-300 px-3 py-2" placeholder="Username" disabled />
        <input className="w-full rounded border border-slate-300 px-3 py-2" placeholder="Password" type="password" disabled />
        <button className="w-full rounded bg-brand-600 px-3 py-2 text-white" disabled>Sign in (disabled)</button>
      </div>
    </div>
  );
}
