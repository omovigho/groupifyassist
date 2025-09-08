import { useEffect, useState } from 'react';
import Layout from '@/components/dashboard/Layout';
import { api } from '@/lib/api';

const Exports = () => {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await api.get('/dashboard/exports/recent?limit=25');
        setRows(data || []);
      } catch {}
    };
    load();
  }, []);

  return (
    <Layout>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-semibold">Recent Exports</h1>
      </div>
  <div className="rounded-2xl bg-white dark:bg-slate-900 shadow-sm border border-slate-200 dark:border-slate-800 overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800">
          <thead className="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400">File</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400">Type</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400">Session</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400">Created</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400">Size</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 dark:divide-slate-800 bg-white dark:bg-slate-900">
            {rows.length === 0 ? (
              <tr><td colSpan={6} className="px-4 py-6 text-sm text-slate-500 dark:text-slate-400">No exports yet.</td></tr>
            ) : rows.map((r)=> (
              <tr key={`e_${r.id}`}>
                <td className="px-4 py-3 text-sm text-slate-700 dark:text-slate-200">{r.file_name}</td>
                <td className="px-4 py-3 text-sm capitalize">{r.file_type}</td>
                <td className="px-4 py-3 text-sm">{r.session_name}</td>
                <td className="px-4 py-3 text-sm">{new Date(r.created_at).toLocaleString()}</td>
                <td className="px-4 py-3 text-sm">{(r.file_size/1024).toFixed(1)} KB</td>
                <td className="px-4 py-3 text-sm text-right">
                  <a href={r.download_url} className="text-[#0A2540] dark:text-sky-400 hover:underline">Download</a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Layout>
  );
};

export default Exports;
