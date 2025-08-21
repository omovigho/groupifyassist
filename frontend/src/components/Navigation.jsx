import { motion } from 'framer-motion';
import { 
  Home,
  Users,
  BarChart3,
  Download,
  Settings,
  Bell,
  LogOut,
  User,
  Menu,
  X
} from 'lucide-react';
import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

const Navigation = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { user, logout } = useAuth();

  const navigationItems = [
    {
      name: 'Dashboard',
      icon: Home,
      href: '/dashboard',
      active: true
    },
    {
      name: 'Sessions',
      icon: Users,
      href: '/sessions',
      active: false
    },
    {
      name: 'Analytics',
      icon: BarChart3,
      href: '/analytics',
      active: false
    },
    {
      name: 'Export Center',
      icon: Download,
      href: '/export',
      active: false
    },
    {
      name: 'Settings',
      icon: Settings,
      href: '/settings',
      active: false
    }
  ];

  const handleLogout = () => {
    logout();
  };

  return (
    <>
      {/* Desktop Navigation - Sidebar */}
      <div className="hidden lg:block fixed left-0 top-0 h-full w-64 bg-white/80 backdrop-blur-lg border-r border-gray-200 z-40">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="p-6">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-2 rounded-xl">
                <Users className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  GroupifyAssist
                </h1>
                <p className="text-xs text-gray-500">Session Management</p>
              </div>
            </div>
          </div>

          {/* Navigation Items */}
          <nav className="flex-1 px-4">
            <ul className="space-y-2">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                return (
                  <li key={item.name}>
                    <motion.a
                      href={item.href}
                      whileHover={{ x: 4 }}
                      className={`flex items-center px-4 py-3 rounded-xl transition-all duration-200 ${
                        item.active
                          ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg'
                          : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                      }`}
                    >
                      <Icon className="w-5 h-5 mr-3" />
                      <span className="font-medium">{item.name}</span>
                    </motion.a>
                  </li>
                );
              })}
            </ul>
          </nav>

          {/* User Profile */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                  <User className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {user?.full_name || user?.email?.split('@')[0]}
                  </p>
                  <p className="text-xs text-gray-500">{user?.email}</p>
                </div>
              </div>
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={handleLogout}
                className="p-2 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-all duration-200"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
              </motion.button>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <div className="lg:hidden">
        {/* Mobile Header */}
        <div className="fixed top-0 left-0 right-0 bg-white/90 backdrop-blur-lg border-b border-gray-200 z-50">
          <div className="flex items-center justify-between px-4 py-3">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-2 rounded-lg">
                <Users className="w-5 h-5" />
              </div>
              <h1 className="text-lg font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                GroupifyAssist
              </h1>
            </div>
            
            <div className="flex items-center space-x-2">
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                className="p-2 text-gray-600 hover:text-blue-600 rounded-lg hover:bg-blue-50"
              >
                <Bell className="w-5 h-5" />
              </motion.button>
              
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="p-2 text-gray-600 hover:text-blue-600 rounded-lg hover:bg-blue-50"
              >
                {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </motion.button>
            </div>
          </div>
        </div>

        {/* Mobile Menu Overlay */}
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
            onClick={() => setIsMobileMenuOpen(false)}
          />
        )}

        {/* Mobile Menu */}
        <motion.div
          initial={{ x: '-100%' }}
          animate={{ x: isMobileMenuOpen ? 0 : '-100%' }}
          transition={{ type: 'spring', damping: 20 }}
          className="fixed top-16 left-0 bottom-0 w-64 bg-white/95 backdrop-blur-lg border-r border-gray-200 z-50"
        >
          <div className="flex flex-col h-full">
            {/* Navigation Items */}
            <nav className="flex-1 px-4 py-6">
              <ul className="space-y-2">
                {navigationItems.map((item) => {
                  const Icon = item.icon;
                  return (
                    <li key={item.name}>
                      <motion.a
                        href={item.href}
                        whileHover={{ x: 4 }}
                        onClick={() => setIsMobileMenuOpen(false)}
                        className={`flex items-center px-4 py-3 rounded-xl transition-all duration-200 ${
                          item.active
                            ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg'
                            : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                        }`}
                      >
                        <Icon className="w-5 h-5 mr-3" />
                        <span className="font-medium">{item.name}</span>
                      </motion.a>
                    </li>
                  );
                })}
              </ul>
            </nav>

            {/* User Profile */}
            <div className="p-4 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                    <User className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {user?.full_name || user?.email?.split('@')[0]}
                    </p>
                    <p className="text-xs text-gray-500">{user?.email}</p>
                  </div>
                </div>
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={handleLogout}
                  className="p-2 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </motion.button>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </>
  );
};

export default Navigation;
