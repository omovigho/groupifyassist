import { useMemo, useState, useEffect } from 'react';
import { Code, Layers3, CheckSquare } from 'lucide-react';
import Layout from '@/components/dashboard/Layout';
import StatCard from '@/components/dashboard/StatCard';
import { api } from '@/lib/api';
import { Link } from 'react-router-dom';

const Overview = () => {
  const [overview, setOverview] = useState(null);
  const [totals, setTotals] = useState({ groups: 0, selections: 0 });
  const [hostStats, setHostStats] = useState({ active_codes_total: 0, total_groups: 0, total_selections: 0 });
  const [hostName, setHostName] = useState('Host');

  useEffect(() => {
    const load = async () => {
      try {
        const [profile, stats] = await Promise.all([
          api.get('/user/profile'),
          api.get('/dashboard/stats'),
        ]);
        setHostName(profile?.data?.email?.split('@')[0] || 'Host');
        setHostStats(stats?.data || { active_codes_total: 0, total_groups: 0, total_selections: 0 });
        setTotals({
          groups: stats?.data?.total_groups || 0,
          selections: stats?.data?.total_selections || 0,
        });
      } catch (e) {
        // handled globally
      }
    };
    load();
  }, []);

  const pieData = useMemo(() => {
  const active = hostStats?.active_codes_total ?? 0;
    const groups = hostStats?.total_groups ?? totals.groups ?? 0;
    const selections = hostStats?.total_selections ?? totals.selections ?? 0;
    return [
      { label: 'Groups', value: groups, color: '#0A2540' },
      { label: 'Selections', value: selections, color: '#00BFA6' },
      { label: 'Active Codes', value: active, color: '#F59E0B' },
    ];
  }, [overview, totals, hostStats]);

  const PieChart = ({ data = [], size = 160, stroke = 16 }) => {
    const total = data.reduce((s, d) => s + d.value, 0) || 1;
    const radius = (size - stroke) / 2;
    let offset = 0;
    return (
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <g transform={`translate(${size / 2}, ${size / 2})`}>
          {/* background ring for visibility when values are zero */}
          <circle r={radius} cx={0} cy={0} fill="transparent" stroke="#E5E7EB" strokeWidth={stroke} />
          {data.map((d, i) => {
            const pct = d.value / total;
            const dash = 2 * Math.PI * radius * pct;
            const gap = 2 * Math.PI * radius - dash;
            const rotation = (offset / total) * 360 - 90;
            offset += d.value;
            return (
              <circle
                key={i}
                r={radius}
                cx={0}
                cy={0}
                fill="transparent"
                stroke={d.color}
                strokeWidth={stroke}
                strokeDasharray={`${dash} ${gap}`}
                transform={`rotate(${rotation})`}
                strokeLinecap="butt"
              />
            );
          })}
        </g>
      </svg>
    );
  };

  return (
    <Layout>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold">Welcome back, {hostName} 👋</h1>
        <p className="text-slate-600 dark:text-slate-300 text-sm mt-1">Your current stats at a glance.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
  <StatCard title="Active Codes" value={hostStats?.active_codes_total ?? overview?.active_sessions ?? 0} icon={Code} color="#F59E0B" />
  <StatCard title="Total Groups" value={hostStats?.total_groups ?? totals.groups ?? 0} icon={Layers3} color="#0A2540" />
  <StatCard title="Total Selections" value={hostStats?.total_selections ?? totals.selections ?? 0} icon={CheckSquare} color="#00BFA6" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
        <div className="rounded-2xl bg-white dark:bg-slate-900 shadow-sm border border-slate-200 dark:border-slate-800 p-4 flex items-center justify-center">
          <div className="flex items-center gap-6">
            <PieChart data={pieData} />
            <div className="text-sm space-y-2">
              {pieData.map((d) => (
                <div key={d.label} className="flex items-center gap-2">
                  <span className="inline-block w-3 h-3 rounded-sm" style={{background:d.color}} />
                  <span className="text-slate-700 dark:text-slate-200">{d.label}:</span>
                  <span className="font-medium">{d.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
        <div className="lg:col-span-2 rounded-2xl bg-white dark:bg-slate-900 shadow-sm border border-slate-200 dark:border-slate-800 p-4 space-y-3">
          <h3 className="text-sm font-medium text-slate-700 dark:text-slate-200">Quick Actions</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <Link to="/dashboard/groups/create" className="rounded-lg bg-[#0A2540] text-white px-4 py-3 text-sm text-center hover:opacity-95">+ Create New Grouping</Link>
            <Link to="/dashboard/selections/create" className="rounded-lg bg-[#00BFA6] text-white px-4 py-3 text-sm text-center hover:opacity-95">🎯 Create New Selection</Link>
            <Link to="/dashboard/selections/make" className="rounded-lg bg-[#0A2540] text-white px-4 py-3 text-sm text-center hover:opacity-95">🧠 Make Selection</Link>
            <Link to="/dashboard/selections/clear" className="rounded-lg bg-[#F59E0B] text-white px-4 py-3 text-sm text-center hover:opacity-95">🧹 Clear Selections</Link>
            <Link to="/dashboard/exports" className="rounded-lg bg-[#0A2540] text-white px-4 py-3 text-sm text-center hover:opacity-95">📤 Export Results</Link>
            <Link to="/logout" className="rounded-lg bg-[#00BFA6] text-white px-4 py-3 text-sm text-center hover:opacity-95">🚪 Logout</Link>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Overview;
