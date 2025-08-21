import { useState, useEffect, useCallback } from 'react';
// eslint-disable-next-line no-unused-vars
import { motion } from 'framer-motion';
import { 
  Users, 
  Activity, 
  BarChart3, 
  Calendar, 
  Bell, 
  Settings,
  Download,
  RefreshCw,
  TrendingUp,
  Clock,
  UserCheck,
  AlertCircle,
  Plus,
  Eye,
  FileText,
  Globe,
  Award,
  Zap,
  Target,
  Map
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';
import WelcomeHero from '../components/WelcomeHero';
import QuickActions from '../components/QuickActions';
import DashboardStats from '../components/DashboardStats';
import Navigation from '../components/Navigation';

const DashboardPage = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [activeSessions, setActiveSessions] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [_analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');

  const { user, token } = useAuth();

  const timeRanges = [
    { value: '7d', label: '7 Days' },
    { value: '30d', label: '30 Days' },
    { value: '90d', label: '90 Days' },
    { value: '1y', label: '1 Year' }
  ];

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError('');

      // Fetch dashboard overview
      const overviewResponse = await fetch('/api/v1/dashboard/overview', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!overviewResponse.ok) {
        throw new Error('Failed to fetch dashboard data');
      }

      const overview = await overviewResponse.json();
      setDashboardData(overview);

      // Fetch active sessions
      const sessionsResponse = await fetch('/api/v1/dashboard/active-sessions', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (sessionsResponse.ok) {
        const sessions = await sessionsResponse.json();
        setActiveSessions(sessions);
      }

      // Fetch notifications
      const notificationsResponse = await fetch('/api/v1/dashboard/notifications', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (notificationsResponse.ok) {
        const notifs = await notificationsResponse.json();
        setNotifications(notifs);
      }

      // Fetch analytics
      const analyticsResponse = await fetch(`/api/v1/dashboard/analytics?period=${selectedTimeRange}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (analyticsResponse.ok) {
        const analyticsData = await analyticsResponse.json();
        setAnalytics(analyticsData);
      }

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [selectedTimeRange, token]);

  const handleQuickAction = (actionId) => {
    console.log('Quick action clicked:', actionId);
    // TODO: Implement navigation logic
    switch (actionId) {
      case 'create-group':
        // Navigate to group session creation
        break;
      case 'create-selection':
        // Navigate to selection session creation
        break;
      case 'view-reports':
        // Navigate to reports/analytics page
        break;
      case 'export-data':
        // Navigate to export center
        break;
      default:
        break;
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        duration: 0.6,
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  if (loading) {
    return <LoadingSpinner text="Loading dashboard..." />;
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="card p-8 text-center max-w-md mx-auto"
        >
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Dashboard</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchDashboardData}
            className="btn-primary flex items-center mx-auto"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Retry
          </button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-100">
      <Navigation />
      
      {/* Main Content - adjust margin for sidebar */}
      <div className="lg:ml-64">
        {/* Header - Mobile spacing */}
        <div className="lg:hidden h-16"></div>
        
        <motion.header 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white/80 backdrop-blur-lg shadow-sm border-b border-white/20 sticky top-0 lg:top-0 z-30"
        >
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center space-x-4">
                <div className="hidden lg:flex items-center space-x-4">
                  <div>
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                      Dashboard Overview
                    </h1>
                    <p className="text-gray-600 text-sm">Monitor your session activities</p>
                  </div>
                </div>
                <div className="lg:hidden">
                  <h1 className="text-xl font-bold text-gray-900">Dashboard</h1>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <select
                  value={selectedTimeRange}
                  onChange={(e) => setSelectedTimeRange(e.target.value)}
                  className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white/80 backdrop-blur-sm"
                >
                  {timeRanges.map((range) => (
                    <option key={range.value} value={range.value}>
                      {range.label}
                    </option>
                  ))}
                </select>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={fetchDashboardData}
                  className="p-2 text-gray-500 hover:text-blue-600 rounded-lg hover:bg-blue-50 transition-all duration-200"
                >
                  <RefreshCw className="w-5 h-5" />
                </motion.button>
                <motion.button 
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="p-2 text-gray-500 hover:text-blue-600 rounded-lg hover:bg-blue-50 relative transition-all duration-200 lg:hidden"
                >
                  <Bell className="w-5 h-5" />
                  {notifications.length > 0 && (
                    <motion.span 
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="absolute -top-1 -right-1 bg-gradient-to-r from-red-500 to-pink-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold"
                    >
                      {notifications.length}
                    </motion.span>
                  )}
                </motion.button>
              </div>
            </div>
          </div>
        </motion.header>

        {/* Main Content */}
        <motion.div
          className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
        {/* Welcome Section */}
        <motion.div variants={itemVariants} className="mb-8">
          <WelcomeHero user={user} dashboardData={dashboardData} />
        </motion.div>

        {/* Quick Action Cards */}
        <motion.div variants={itemVariants} className="mb-8">
          <QuickActions onActionClick={handleQuickAction} />
        </motion.div>

        {/* Stats Grid */}
        <motion.div variants={itemVariants} className="mb-8">
          <DashboardStats data={dashboardData} loading={loading} />
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Active Sessions */}
          <motion.div variants={itemVariants} className="lg:col-span-2">
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/50">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-gray-900">Active Sessions</h3>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">Session Building</span>
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </div>
              </div>
              
              {activeSessions.length > 0 ? (
                <div className="space-y-4">
                  {activeSessions.slice(0, 5).map((session, index) => (
                    <motion.div
                      key={session.id || index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-blue-50 rounded-xl border border-blue-100 hover:shadow-md transition-all duration-200"
                    >
                      <div className="flex items-center">
                        <div className="bg-gradient-to-br from-blue-500 to-indigo-600 p-3 rounded-xl mr-4">
                          <Users className="w-5 h-5 text-white" />
                        </div>
                        <div>
                          <p className="font-semibold text-gray-900">
                            {session.session_name || `Session ${session.id}`}
                          </p>
                          <p className="text-sm text-gray-600">
                            {session.participants_count || 0} participants • Building
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className="px-3 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                          Active
                        </span>
                        <button className="p-2 text-gray-400 hover:text-blue-600 rounded-lg hover:bg-blue-50">
                          <Eye className="w-4 h-4" />
                        </button>
                      </div>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="bg-gray-100 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4">
                    <Activity className="w-10 h-10 text-gray-400" />
                  </div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">No Active Sessions</h4>
                  <p className="text-gray-500 mb-4">Create your first session to get started</p>
                  <button className="btn-primary">
                    <Plus className="w-4 h-4 mr-2" />
                    Create Session
                  </button>
                </div>
              )}
            </div>
          </motion.div>

          {/* Recent Activity */}
          <motion.div variants={itemVariants}>
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/50">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-gray-900">Recent Activity</h3>
                <div className="flex items-center text-sm text-gray-500">
                  <Clock className="w-4 h-4 mr-1" />
                  Live updates
                </div>
              </div>
              
              {notifications.length > 0 ? (
                <div className="space-y-4">
                  {notifications.slice(0, 6).map((notification, index) => (
                    <motion.div
                      key={notification.id || index}
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-start space-x-3 p-3 rounded-xl hover:bg-gray-50 transition-colors duration-200"
                    >
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                          <div className="w-2 h-2 bg-white rounded-full"></div>
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900">
                          {notification.title || 'New Activity'}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {notification.message || notification.content || 'Recent system activity'}
                        </p>
                        <p className="text-xs text-gray-400 mt-1">
                          {notification.created_at || 'Just now'}
                        </p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="bg-gray-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                    <Bell className="w-8 h-8 text-gray-400" />
                  </div>
                  <h4 className="text-sm font-medium text-gray-900 mb-1">No Recent Activity</h4>
                  <p className="text-xs text-gray-500">Activity will appear here</p>
                </div>
              )}
            </div>
          </motion.div>
        </div>

        {/* Analytics Overview */}
        <motion.div variants={itemVariants} className="mt-8">
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/50">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900">Analytics Overview</h3>
              <div className="flex items-center space-x-2">
                <button className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors duration-200">
                  View Details
                </button>
                <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-50">
                  <BarChart3 className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-full w-24 h-24 flex items-center justify-center mx-auto mb-4">
                  <TrendingUp className="w-12 h-12 text-white" />
                </div>
                <h4 className="text-lg font-semibold text-gray-900 mb-1">Growth Rate</h4>
                <p className="text-2xl font-bold text-green-600">+24%</p>
                <p className="text-sm text-gray-500">This month</p>
              </div>

              <div className="text-center">
                <div className="bg-gradient-to-br from-blue-500 to-cyan-600 rounded-full w-24 h-24 flex items-center justify-center mx-auto mb-4">
                  <Users className="w-12 h-12 text-white" />
                </div>
                <h4 className="text-lg font-semibold text-gray-900 mb-1">User Engagement</h4>
                <p className="text-2xl font-bold text-blue-600">92%</p>
                <p className="text-sm text-gray-500">Satisfaction rate</p>
              </div>

              <div className="text-center">
                <div className="bg-gradient-to-br from-purple-500 to-indigo-600 rounded-full w-24 h-24 flex items-center justify-center mx-auto mb-4">
                  <Map className="w-12 h-12 text-white" />
                </div>
                <h4 className="text-lg font-semibold text-gray-900 mb-1">Global Reach</h4>
                <p className="text-2xl font-bold text-purple-600">12</p>
                <p className="text-sm text-gray-500">Countries served</p>
              </div>
            </div>
          </div>
        </motion.div>
        </motion.div>
      </div>
    </div>
  );
};

export default DashboardPage;
