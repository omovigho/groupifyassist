import { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { User, Menu, X } from 'lucide-react';
import ThemeToggle from '@/components/ThemeToggle';

const Navbar = () => {
  const [open, setOpen] = useState(false);
  const items = [
    {to: '/dashboard', label: 'Dashboard'},
    {to: '/dashboard/groups', label: 'Groups'},
    {to: '/dashboard/selections', label: 'Selections'},
    {to: '/dashboard/exports', label: 'Reports'},
    {to: '/dashboard/settings', label: 'Settings'},
  ];
  return (
  <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-white dark:bg-slate-900/60 dark:border-slate-800 backdrop-blur supports-[backdrop-filter]:bg-white/70 supports-[backdrop-filter]:dark:bg-slate-900/60">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link to="/dashboard" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-[#0A2540]" />
            <span className="font-semibold text-[#0A2540]">GroupifyAssist</span>
          </Link>
          <nav className="hidden md:flex items-center gap-4 ml-8 text-sm text-slate-600 dark:text-slate-300">
            {items.map((item) => (
              <NavLink key={item.to} to={item.to} className={({isActive})=>`hover:text-[#0A2540] dark:hover:text-sky-400 ${isActive? 'text-[#0A2540] dark:text-sky-400 font-medium':'text-slate-600 dark:text-slate-300'}`}>{item.label}</NavLink>
            ))}
          </nav>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            className="md:hidden inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800"
            aria-label="Toggle navigation menu"
            aria-expanded={open}
            onClick={()=>setOpen(!open)}
          >
            {open ? <X size={18} /> : <Menu size={18} />}
          </button>
          <ThemeToggle />
          <Link to="/dashboard/settings" className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300 hover:text-[#0A2540] dark:hover:text-sky-400">
            <User size={18} />
            <span>My Account</span>
          </Link>
        </div>
      </div>
      {/* Mobile nav */}
      {open && (
        <div className="md:hidden border-t border-slate-200 dark:border-slate-800 bg-white/95 dark:bg-slate-900/95 backdrop-blur">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-3">
            <nav className="grid grid-cols-1 gap-1 text-sm">
              {items.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  onClick={()=>setOpen(false)}
                  className={({isActive})=>`px-3 py-2 rounded-lg ${isActive ? 'bg-slate-100 dark:bg-slate-800 text-[#0A2540] dark:text-sky-400' : 'text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800'}`}
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>
        </div>
      )}
    </header>
  );
};

export default Navbar;
