import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Users, Code, Clock, Layers3 } from 'lucide-react';
import Layout from '@/components/dashboard/Layout';
import StatCard from '@/components/dashboard/StatCard';
import ActivityTable from '@/components/dashboard/ActivityTable';
import ActiveProjects from '@/components/dashboard/ActiveProjects';
import { api } from '@/lib/api';
import { Link } from 'react-router-dom';

const Overview = () => {
  const [overview, setOverview] = useState(null);
  const [activity, setActivity] = useState([]);
  const [hostName, setHostName] = useState('Host');

  useEffect(() => {
    const load = async () => {
      try {
        const [ov, act, profile] = await Promise.all([
          api.get('/dashboard/overview'),
          api.get('/dashboard/user-activity?days=7&limit=10'),
          api.get('/user/profile'),
        ]);
        setOverview(ov.data);
        setActivity(act.data || []);
        setHostName(profile?.data?.email?.split('@')[0] || 'Host');
      } catch (e) {
        // handled globally
      }
    };
    load();
  }, []);

  return (
    <Layout>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold">Welcome back, {hostName} 👋</h1>
        <p className="text-slate-600 text-sm mt-1">Here’s what’s happening with your projects today.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
  <StatCard title="Total Groups" value={overview?.sessions_created ?? 0} icon={Layers3} color="#0A2540" />
  <StatCard title="Total Members" value={overview?.total_participants ?? 0} icon={Users} color="#0A2540" />
  <StatCard title="Active Codes" value={overview?.active_sessions ?? 0} icon={Code} color="#0A2540" />
  <StatCard title="Completed Groups" value={overview?.completed_groups ?? 0} icon={Clock} color="#0A2540" />
      </div>

      <div className="mt-6">
        <ActiveProjects />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
        <motion.div initial={{opacity:0,y:8}} animate={{opacity:1,y:0}} transition={{duration:0.35}} className="lg:col-span-2">
          <ActivityTable items={activity} />
        </motion.div>
        <motion.div initial={{opacity:0,y:8}} animate={{opacity:1,y:0}} transition={{duration:0.35}} className="space-y-3">
          <h3 className="text-sm font-medium text-slate-700">Quick Actions</h3>
          <div className="grid grid-cols-1 gap-3">
            <Link to="/dashboard/groups/create" className="rounded-lg bg-[#0A2540] text-white px-4 py-3 text-sm text-center hover:opacity-95">+ Create New Grouping</Link>
            <Link to="/dashboard/selections/create" className="rounded-lg bg-[#00BFA6] text-white px-4 py-3 text-sm text-center hover:opacity-95">🎯 Create New Selection</Link>
            <button disabled className="rounded-lg bg-slate-200 text-slate-500 px-4 py-3 text-sm text-left">📂 Import Members (coming soon)</button>
            <Link to="/dashboard/exports" className="rounded-lg bg-white border border-slate-200 px-4 py-3 text-sm text-left hover:bg-slate-50">📤 Export Results</Link>
          </div>
        </motion.div>
      </div>
    </Layout>
  );
};

export default Overview;
