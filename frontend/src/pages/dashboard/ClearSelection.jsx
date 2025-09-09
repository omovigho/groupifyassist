import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import Layout from '@/components/dashboard/Layout';
import { api } from '@/lib/api';

const ClearSelection = () => {
  const location = useLocation();
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const onSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');
    if (!code.trim()) {
      setError('Please enter a valid selection access code.');
      return;
    }
    try {
      setLoading(true);
      const { data } = await api.post('/selections/clear', null, { params: { code: code.trim() } });
      setMessage(data?.message || 'Selections cleared successfully.');
    } catch (e) {
      const msg = e?.response?.data?.detail || 'Failed to clear selections. Check the code and try again.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      {/* Tabs: Make vs Clear Selection */}
      {(() => {
        const isClear = location.pathname.includes('/selections/clear');
        return (
          <div className="mb-4 flex items-center gap-2">
            <Link to="/dashboard/selections/make" className={`rounded-md px-3 py-2 text-sm ${!isClear ? 'bg-[#0A2540] text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200'}`}>🎯 Make Selection</Link>
            <Link to="/dashboard/selections/clear" className={`rounded-md px-3 py-2 text-sm ${isClear ? 'bg-[#F59E0B] text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200'}`}>🧹 Clear Selection</Link>
          </div>
        );
      })()}
      <div className="rounded-2xl bg-[#F59E0B] text-white px-4 py-3 mb-4">
        <h1 className="text-xl font-semibold">Clear Selection</h1>
        <p className="text-sm opacity-90">Enter a selection access code to clear all previous selections for that session.</p>
      </div>
      <form onSubmit={onSubmit} className="rounded-2xl bg-white dark:bg-slate-900 shadow-sm border border-slate-200 dark:border-slate-800 p-4 space-y-4">
        {error && <div className="rounded-md bg-red-50 border border-red-200 text-red-700 px-3 py-2 text-sm">{error}</div>}
        {message && <div className="rounded-md bg-green-50 border border-green-200 text-green-700 px-3 py-2 text-sm">{message}</div>}
        <div>
          <label className="block text-xs font-medium text-slate-600 dark:text-slate-300 mb-1">Access Code</label>
          <input value={code} onChange={(e)=>setCode(e.target.value)} placeholder="e.g., ABC123" className="h-10 w-full rounded-md border border-slate-300 px-3 text-sm bg-white dark:bg-white text-black dark:text-black placeholder:text-slate-400" />
        </div>
  <button type="submit" disabled={loading} className="rounded-md bg-[#F59E0B] text-white text-sm px-4 py-2 disabled:opacity-60">{loading ? 'Clearing…' : 'Clear Selections'}</button>
      </form>
    </Layout>
  );
};

export default ClearSelection;
