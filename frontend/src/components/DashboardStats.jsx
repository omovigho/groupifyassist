import { motion } from 'framer-motion';
import { 
  Users, 
  Activity, 
  TrendingUp, 
  UserCheck,
  Clock,
  Globe,
  Award,
  Target
} from 'lucide-react';

const DashboardStats = ({ data, loading = false }) => {
  const stats = [
    {
      title: 'Total Sessions',
      value: data?.total_sessions || 0,
      change: '+12%',
      changeType: 'positive',
      icon: Users,
      color: 'from-blue-500 to-blue-600',
      bgColor: 'from-blue-50 to-blue-100'
    },
    {
      title: 'Active Sessions',
      value: data?.active_sessions || 0,
      change: '+8%',
      changeType: 'positive',
      icon: Activity,
      color: 'from-green-500 to-green-600',
      bgColor: 'from-green-50 to-green-100'
    },
    {
      title: 'Total Participants',
      value: data?.total_participants || 0,
      change: 'Across all sessions',
      changeType: 'neutral',
      icon: UserCheck,
      color: 'from-purple-500 to-purple-600',
      bgColor: 'from-purple-50 to-purple-100'
    },
    {
      title: 'Success Rate',
      value: data?.success_rate || '98%',
      change: 'Session completion',
      changeType: 'positive',
      icon: TrendingUp,
      color: 'from-orange-500 to-orange-600',
      bgColor: 'from-orange-50 to-orange-100'
    }
  ];

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, index) => (
          <div key={index} className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/50">
            <div className="animate-pulse">
              <div className="flex items-center justify-between">
                <div>
                  <div className="h-4 bg-gray-200 rounded w-24 mb-2"></div>
                  <div className="h-8 bg-gray-200 rounded w-16 mb-1"></div>
                  <div className="h-3 bg-gray-200 rounded w-20"></div>
                </div>
                <div className="w-12 h-12 bg-gray-200 rounded-xl"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <motion.div
      variants={{
        hidden: { opacity: 0 },
        visible: {
          opacity: 1,
          transition: {
            staggerChildren: 0.1
          }
        }
      }}
      initial="hidden"
      animate="visible"
      className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
    >
      {stats.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <motion.div 
            key={stat.title}
            variants={itemVariants}
            whileHover={{ scale: 1.02, y: -2 }}
            className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/50 hover:shadow-xl transition-all duration-300"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600 mb-1">{stat.title}</p>
                <p className="text-3xl font-bold text-gray-900 mb-1">
                  {stat.value}
                </p>
                <p className={`text-sm ${
                  stat.changeType === 'positive' 
                    ? 'text-green-600' 
                    : stat.changeType === 'negative' 
                      ? 'text-red-600' 
                      : 'text-blue-600'
                }`}>
                  {stat.change}
                </p>
              </div>
              <div className={`bg-gradient-to-br ${stat.color} p-3 rounded-xl shadow-lg`}>
                <Icon className="w-8 h-8 text-white" />
              </div>
            </div>

            {/* Progress bar for visual appeal */}
            <div className="mt-4">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <motion.div 
                  className={`bg-gradient-to-r ${stat.color} h-2 rounded-full`}
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(100, (stat.value / 100) * 100)}%` }}
                  transition={{ duration: 1, delay: index * 0.2 }}
                />
              </div>
            </div>
          </motion.div>
        );
      })}
    </motion.div>
  );
};

export default DashboardStats;
