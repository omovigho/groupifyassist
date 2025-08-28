import { Link, NavLink } from 'react-router-dom';
import { User } from 'lucide-react';
import ThemeToggle from '@/components/ThemeToggle';

const Navbar = () => {
  return (
  <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-white dark:bg-slate-900/60 dark:border-slate-800 backdrop-blur supports-[backdrop-filter]:bg-white/70 supports-[backdrop-filter]:dark:bg-slate-900/60">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link to="/dashboard" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-[#0A2540]" />
            <span className="font-semibold text-[#0A2540]">GroupifyAssist</span>
          </Link>
          <nav className="hidden md:flex items-center gap-4 ml-8 text-sm text-slate-600 dark:text-slate-300">
            {[
              {to: '/dashboard', label: 'Dashboard'},
              {to: '/dashboard/groups', label: 'Groups'},
              {to: '/dashboard/selections', label: 'Selections'},
              {to: '/dashboard/exports', label: 'Reports'},
              {to: '/dashboard/settings', label: 'Settings'},
            ].map((item) => (
              <NavLink key={item.to} to={item.to} className={({isActive})=>`hover:text-[#0A2540] dark:hover:text-sky-400 ${isActive? 'text-[#0A2540] dark:text-sky-400 font-medium':'text-slate-600 dark:text-slate-300'}`}>{item.label}</NavLink>
            ))}
          </nav>
        </div>
        <div className="flex items-center gap-4">
          <ThemeToggle />
          <Link to="/dashboard/settings" className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300 hover:text-[#0A2540] dark:hover:text-sky-400">
            <User size={18} />
            <span>My Account</span>
          </Link>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
