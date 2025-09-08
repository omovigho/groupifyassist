import { useLocation, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import Layout from '@/components/dashboard/Layout';
import { CheckCircle2, Copy } from 'lucide-react';

export default function CreateSuccess() {
  const { state } = useLocation();
  const session = state?.session;
  const code = session?.code_id;

  const copy = async () => {
    if (!code) return;
    try { await navigator.clipboard.writeText(code); } catch {}
  };

  return (
    <Layout>
      <motion.div initial={{opacity:0,y:12}} animate={{opacity:1,y:0}} transition={{duration:0.35}} className="max-w-2xl mx-auto text-center">
        <div className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-8">
          <div className="flex justify-center mb-4">
            <CheckCircle2 size={56} className="text-emerald-500" />
          </div>
          <h1 className="text-2xl font-semibold">Session Created Successfully</h1>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-2">Share the access code with your participants. You can also manage the project from your dashboard.</p>
          <div className="mt-6 inline-flex items-center gap-3 rounded-xl border border-slate-300 dark:border-slate-700 px-4 py-3 bg-slate-50 dark:bg-slate-800">
            <span className="font-mono text-lg">{code || '—'}</span>
            <button onClick={copy} className="text-slate-600 hover:text-slate-900 dark:text-slate-300"><Copy size={18} /></button>
          </div>
          <div className="mt-6 grid grid-cols-2 gap-4 text-left text-sm">
            <div className="rounded-lg border border-slate-200 dark:border-slate-800 p-4">
              <p className="text-slate-500">Name</p>
              <p className="font-medium">{session?.name}</p>
            </div>
            <div className="rounded-lg border border-slate-200 dark:border-slate-800 p-4">
              <p className="text-slate-500">Max</p>
              <p className="font-medium">{session?.max}</p>
            </div>
          </div>
          <div className="mt-8 flex justify-center gap-3">
            <Link to="/dashboard" className="px-4 py-2 rounded-md bg-slate-800 text-white">Go to Dashboard</Link>
            <Link to="/dashboard/exports" className="px-4 py-2 rounded-md border border-slate-300 dark:border-slate-700">View Reports</Link>
          </div>
        </div>
      </motion.div>
    </Layout>
  );
}
