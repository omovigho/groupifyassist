import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import Layout from '@/components/dashboard/Layout';
import { api } from '@/lib/api';

const MakeSelection = () => {
  const location = useLocation();
  const [code, setCode] = useState('');
  const [count, setCount] = useState(1);
  const [prefKey, setPrefKey] = useState('');
  const [prefValue, setPrefValue] = useState('');
  const [prefMax, setPrefMax] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const canSubmit = () => {
    if (!code || !count || count <= 0) return false;
    if (prefMax) {
      const max = Number(prefMax);
      if (Number.isFinite(max) && max > Number(count)) return false;
    }
    return true;
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);
    const c = Number(count);
    if (!c || c <= 0) {
      setError('Count must be a positive number.');
      return;
    }
    if (prefMax) {
      const max = Number(prefMax);
      if (!Number.isFinite(max) || max < 0) {
        setError('Preferential max must be a non-negative number.');
        return;
      }
      if (max > c) {
        setError('Preferential max cannot be greater than Count.');
        return;
      }
    }
    try {
      setLoading(true);
      const payload = {
        code: code.trim(),
        count: c,
        ...(prefKey && prefValue ? { preferential_selection: { [prefKey.trim()]: String(prefValue).trim() } } : {}),
      };
      // Note: prefMax is validated client-side for UX, actual max enforcement follows session rules on server
      const { data } = await api.post('/selections/select', payload);
      setResult(data);
    } catch (e) {
      const msg = e?.response?.data?.detail || 'Selection failed. Check your code and try again.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      {/* Tabs: Make vs Clear Selection */}
      {(() => {
        const isMake = location.pathname.includes('/selections/make');
        return (
          <div className="mb-4 flex items-center gap-2">
            <Link to="/dashboard/selections/make" className={`rounded-md px-3 py-2 text-sm ${isMake ? 'bg-[#0A2540] text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200'}`}>🎯 Make Selection</Link>
            <Link to="/dashboard/selections/clear" className={`rounded-md px-3 py-2 text-sm ${!isMake ? 'bg-[#F59E0B] text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200'}`}>🧹 Clear Selection</Link>
          </div>
        );
      })()}
      <div className="rounded-2xl bg-[#0A2540] text-white px-4 py-3 mb-4">
        <h1 className="text-xl font-semibold">Make Selection</h1>
        <p className="text-sm opacity-90">Select members for an active selection session using its access code. Optionally prioritize a field/value.</p>
      </div>

      <form onSubmit={onSubmit} className="rounded-2xl bg-white dark:bg-slate-900 shadow-sm border border-slate-200 dark:border-slate-800 p-4 space-y-4">
        {error && (
          <div className="rounded-md bg-red-50 border border-red-200 text-red-700 px-3 py-2 text-sm">{error}</div>
        )}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-600 dark:text-slate-300 mb-1">Access Code</label>
            <input value={code} onChange={(e)=>setCode(e.target.value)} placeholder="e.g., ABC123" className="h-10 w-full rounded-md border border-slate-300 px-3 text-sm bg-white dark:bg-white text-black dark:text-black placeholder:text-slate-400" />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-600 dark:text-slate-300 mb-1">Count</label>
            <input type="number" min={1} value={count} onChange={(e)=>setCount(Number(e.target.value))} className="h-10 w-full rounded-md border border-slate-300 px-3 text-sm bg-white dark:bg-white text-black dark:text-black" />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-600 dark:text-slate-300 mb-1">Preferential Field Key (optional)</label>
            <input value={prefKey} onChange={(e)=>setPrefKey(e.target.value)} placeholder="e.g., gender" className="h-10 w-full rounded-md border border-slate-300 px-3 text-sm bg-white dark:bg-white text-black dark:text-black placeholder:text-slate-400" />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-600 dark:text-slate-300 mb-1">Preferential Value (optional)</label>
            <input value={prefValue} onChange={(e)=>setPrefValue(e.target.value)} placeholder="e.g., female" className="h-10 w-full rounded-md border border-slate-300 px-3 text-sm bg-white dark:bg-white text-black dark:text-black placeholder:text-slate-400" />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-600 dark:text-slate-300 mb-1">Preferential Max (optional)</label>
            <input type="number" min={0} value={prefMax} onChange={(e)=>setPrefMax(e.target.value)} className="h-10 w-full rounded-md border border-slate-300 px-3 text-sm bg-white dark:bg-white text-black dark:text-black" />
            <p className="text-xs text-slate-500 mt-1">Must be ≤ Count. Actual max is enforced by your session’s rules.</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button type="submit" disabled={!canSubmit() || loading} className="rounded-md bg-[#00BFA6] text-white text-sm px-4 py-2 disabled:opacity-60">
            {loading ? 'Selecting…' : 'Run Selection'}
          </button>
        </div>
      </form>

      {result && (
        <div className="mt-6 rounded-2xl bg-white dark:bg-slate-900 shadow-sm border border-slate-200 dark:border-slate-800 p-4">
          <h3 className="text-sm font-medium text-slate-700 dark:text-slate-200">Result</h3>
          <div className="mt-3 grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
            <div className="rounded-lg border border-slate-200 dark:border-slate-800 p-3"><div className="text-slate-500">Selected</div><div className="text-lg font-semibold">{result.selected_count}</div></div>
            <div className="rounded-lg border border-slate-200 dark:border-slate-800 p-3"><div className="text-slate-500">Preferential</div><div className="text-lg font-semibold">{result.preferential_count}</div></div>
            <div className="rounded-lg border border-slate-200 dark:border-slate-800 p-3"><div className="text-slate-500">Random</div><div className="text-lg font-semibold">{result.random_count}</div></div>
          </div>
          {Array.isArray(result.member_identifiers) && result.member_identifiers.length > 0 && (
            <div className="mt-4">
              <div className="text-xs font-medium text-slate-600 dark:text-slate-300 mb-1">Selected Member IDs</div>
              <div className="rounded-md border border-slate-200 dark:border-slate-800 p-3 text-sm whitespace-pre-wrap break-words">{result.member_identifiers.join(', ')}</div>
            </div>
          )}
        </div>
      )}
    </Layout>
  );
};

export default MakeSelection;
