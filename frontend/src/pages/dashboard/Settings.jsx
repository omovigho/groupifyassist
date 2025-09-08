import { useEffect, useMemo, useState } from 'react';
import Layout from '@/components/dashboard/Layout';
import { api } from '@/lib/api';
import ThemeToggle from '@/components/ThemeToggle';

const Settings = () => {
  const [prefs, setPrefs] = useState(null);

  useEffect(()=>{
    const load = async ()=>{
      try {
        const { data } = await api.get('/settings/dashboard-preferences');
        setPrefs(data);
      } catch {}
    };
    load();
  },[]);

  const currentTheme = useMemo(() => {
    if (typeof document === 'undefined') return 'light';
    return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
  }, [prefs]);

  return (
    <Layout>
      <h1 className="text-xl font-semibold mb-4">Settings</h1>
      <div className="rounded-2xl bg-white dark:bg-slate-900 shadow-sm border border-slate-200 dark:border-slate-800 p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-slate-700 dark:text-slate-300">Theme</p>
            <p className="text-xs text-slate-500 dark:text-slate-400">Current: <span className="font-medium">{currentTheme}</span></p>
          </div>
          <ThemeToggle />
        </div>
        <p className="text-sm text-slate-700 dark:text-slate-300">Default Session Type: <span className="font-medium">{prefs?.default_session_type}</span></p>
        <p className="text-sm text-slate-700 dark:text-slate-300">Auto Refresh: <span className="font-medium">{prefs?.auto_refresh_interval}s</span></p>
      </div>
    </Layout>
  );
};

export default Settings;
