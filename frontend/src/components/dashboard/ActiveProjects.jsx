import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { api } from '@/lib/api';
import { Link } from 'react-router-dom';

const ActiveProjects = () => {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await api.get('/dashboard/sessions/active?session_type=all&limit=10');
        setRows(data || []);
      } catch {
        setRows([]);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <motion.div initial={{opacity:0,y:8}} animate={{opacity:1,y:0}} transition={{duration:0.35}} className="rounded-2xl bg-white dark:bg-slate-900 shadow-sm border border-slate-200 dark:border-slate-800 overflow-x-auto">
      <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
        <h3 className="text-sm font-medium text-slate-700 dark:text-slate-200">Ongoing Projects</h3>
        <div className="text-xs text-slate-500 dark:text-slate-400">{rows.length} active</div>
      </div>
      <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800">
        <thead className="bg-slate-50 dark:bg-slate-900">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400">Project Name</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400">Type</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400">Created On</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400">Participants</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400">Status</th>
            <th className="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 dark:divide-slate-800 bg-white dark:bg-slate-900">
          {loading ? (
            <tr><td colSpan={6} className="px-4 py-6 text-sm text-slate-500 dark:text-slate-400">Loading…</td></tr>
          ) : rows.length === 0 ? (
            <tr><td colSpan={6} className="px-4 py-6 text-sm text-slate-500 dark:text-slate-400">No ongoing projects.</td></tr>
          ) : rows.map((r)=> (
            <tr key={`${r.type}_${r.id}`}>
              <td className="px-4 py-3 text-sm text-slate-700 dark:text-slate-200">{r.name}</td>
              <td className="px-4 py-3 text-sm capitalize">{r.type}</td>
              <td className="px-4 py-3 text-sm">{r.created_at ? new Date(r.created_at).toLocaleDateString() : '-'}</td>
              <td className="px-4 py-3 text-sm">{r.participant_count ?? 0}</td>
              <td className="px-4 py-3 text-sm capitalize"><span className="inline-flex items-center rounded-full bg-slate-100 dark:bg-slate-800 px-2 py-0.5 text-xs text-slate-700 dark:text-slate-300">{r.status || 'active'}</span></td>
              <td className="px-4 py-3 text-sm text-right">
                <Link to={`/dashboard/projects/${r.type}/${r.id}`} className="text-[#0A2540] dark:text-sky-400 hover:underline">Manage</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </motion.div>
  );
};

export default ActiveProjects;
