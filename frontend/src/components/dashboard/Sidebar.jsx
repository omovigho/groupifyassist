import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Users, Target, FileDown, Settings } from 'lucide-react';

const Sidebar = () => {
  const items = [
    { to: '/dashboard', label: 'Dashboard Overview', icon: LayoutDashboard },
    { to: '/dashboard/groups', label: 'Groups', icon: Users },
    { to: '/dashboard/selections', label: 'Selections', icon: Target },
    { to: '/dashboard/exports', label: 'Exports', icon: FileDown },
  { to: '/dashboard/settings', label: 'Settings', icon: Settings },
  { to: '/logout', label: 'Logout', icon: Settings },
  ];

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden md:flex md:w-64 lg:w-72 shrink-0 bg-[#0A2540] text-white dark:bg-slate-900 dark:text-slate-100 min-h-[calc(100vh-4rem)]">
        <nav className="w-full p-4 space-y-1">
          {items.map(({to, label, icon: Icon}) => (
            <NavLink
              key={to}
              to={to}
              className={({isActive}) => `flex items-center gap-3 px-3 py-2 rounded-lg transition hover:bg-white/10 dark:hover:bg-slate-800/70 ${isActive ? 'bg-white/10 dark:bg-slate-800/70' : ''}`}
            >
              <Icon size={18} />
              <span className="text-sm">{label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>
      {/* Mobile quick nav strip (optional) */}
      <div className="md:hidden -mx-4 mb-4 overflow-x-auto">
        <div className="px-4 min-w-max flex gap-2">
          {items.map(({to, label}) => (
            <NavLink
              key={to}
              to={to}
              className={({isActive}) => `whitespace-nowrap text-xs px-3 py-2 rounded-full border ${isActive ? 'bg-[#0A2540] text-white border-[#0A2540]' : 'border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-200'}`}
            >
              {label.replace(' Overview','')}
            </NavLink>
          ))}
        </div>
      </div>
    </>
  );
};

export default Sidebar;
