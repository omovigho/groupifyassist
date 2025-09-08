import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Layout from '@/components/dashboard/Layout';
import { api } from '@/lib/api';

const Selections = () => {
  const [rows, setRows] = useState([]);
  const [q, setQ] = useState('');
  const [page, setPage] = useState(0);
  const [limit, setLimit] = useState(10);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    const load = async () => {
      try {
        const params = new URLSearchParams({ session_type: 'selection', limit: String(limit), offset: String(page*limit) });
        if (q) params.set('q', q);
        const { data } = await api.get(`/dashboard/sessions/history?${params.toString()}`);
        setRows(data?.sessions || []);
        setTotal(data?.total_count || 0);
      } catch {}
    };
    const id = setTimeout(load, 250);
    return () => clearTimeout(id);
  }, [q, page, limit]);

  return (
    <Layout>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-semibold">Selections</h1>
        <div className="flex items-center gap-2">
          <input value={q} onChange={(e)=>{ setPage(0); setQ(e.target.value); }} placeholder="Search..." className="h-9 rounded-md border border-slate-300 px-3 text-sm" />
          <Link to="/dashboard/selections/create" className="rounded-md bg-[#00BFA6] text-white text-sm px-3 py-2">+ New Selection</Link>
        </div>
      </div>
  <div className="rounded-2xl bg-white dark:bg-slate-900 shadow-sm border border-slate-200 dark:border-slate-800 overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800">
          <thead className="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400">Project Name</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400">Created On</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400">Participants</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400">Status</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400">Access code</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400">Selected</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 dark:divide-slate-800 bg-white dark:bg-slate-900">
            {rows.length === 0 ? (
              <tr><td colSpan={6} className="px-4 py-6 text-sm text-slate-500 dark:text-slate-400">No selection projects yet.</td></tr>
            ) : rows.map((r)=> (
              <tr key={`s_${r.id}`}>
                <td className="px-4 py-3 text-sm text-slate-700 dark:text-slate-200">{r.name}</td>
                <td className="px-4 py-3 text-sm text-slate-600 dark:text-slate-300">{new Date(r.created_at).toLocaleString()}</td>
                <td className="px-4 py-3 text-sm">{r.participant_count}</td>
                <td className="px-4 py-3 text-sm capitalize"><span className="inline-flex items-center rounded-full bg-slate-100 dark:bg-slate-800 px-2 py-0.5 text-xs text-slate-700 dark:text-slate-300">{r.status}</span></td>
                <td className="px-4 py-3 text-sm font-mono">{r.access_code}</td>
                <td className="px-4 py-3 text-sm">{r.selected ?? '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="flex items-center justify-between px-4 py-3 border-t border-slate-200 dark:border-slate-800">
          <span className="text-xs text-slate-600 dark:text-slate-400">Page {page+1} of {Math.max(1, Math.ceil(total/limit))}</span>
          <div className="flex items-center gap-2">
            <button className="px-3 py-1.5 rounded-md border text-sm disabled:opacity-50" disabled={page===0} onClick={()=>setPage(p=>Math.max(0,p-1))}>Previous</button>
            <button className="px-3 py-1.5 rounded-md border text-sm disabled:opacity-50" disabled={(page+1)*limit>=total} onClick={()=>setPage(p=>p+1)}>Next</button>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Selections;
