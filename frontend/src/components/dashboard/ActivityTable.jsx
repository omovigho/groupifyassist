import { motion } from 'framer-motion';

const ActivityTable = ({ items = [] }) => {
  return (
    <motion.div initial={{opacity:0,y:8}} animate={{opacity:1,y:0}} transition={{duration:0.35}} className="rounded-2xl bg-white dark:bg-slate-900 shadow-sm border border-slate-200 dark:border-slate-800">
      <div className="p-4 border-b border-slate-200 dark:border-slate-800">
        <h3 className="text-sm font-medium text-slate-700 dark:text-slate-200">Recent Activity</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800">
          <thead className="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400">Description</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400">Session</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400">Type</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400">When</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 dark:divide-slate-800 bg-white dark:bg-slate-900">
            {items.length === 0 ? (
              <tr><td colSpan={4} className="px-4 py-6 text-sm text-slate-500 dark:text-slate-400">No recent activity</td></tr>
            ) : items.map((it)=> (
              <tr key={it.id}>
                <td className="px-4 py-3 text-sm text-slate-700 dark:text-slate-200">{it.description}</td>
                <td className="px-4 py-3 text-sm text-slate-600 dark:text-slate-300">{it.session_name}</td>
                <td className="px-4 py-3 text-sm capitalize"><span className="inline-flex items-center rounded-full bg-slate-100 dark:bg-slate-800 px-2 py-0.5 text-xs text-slate-700 dark:text-slate-300">{it.session_type}</span></td>
                <td className="px-4 py-3 text-sm text-slate-500 dark:text-slate-400">{new Date(it.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
};

export default ActivityTable;
