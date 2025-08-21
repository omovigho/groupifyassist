import { motion } from 'framer-motion';
import { 
  Plus,
  Target,
  Eye,
  Download,
  Users,
  BarChart3,
  Settings,
  Zap
} from 'lucide-react';

const QuickActions = ({ onActionClick }) => {
  const actions = [
    {
      id: 'create-group',
      title: 'Create',
      subtitle: 'Group Session',
      description: 'Start a new group session',
      icon: Plus,
      gradient: 'from-green-500 to-emerald-600',
      hoverGradient: 'from-green-600 to-emerald-700'
    },
    {
      id: 'create-selection',
      title: 'Create',
      subtitle: 'Selection Session',
      description: 'Selection & grouping',
      icon: Target,
      gradient: 'from-blue-500 to-cyan-600',
      hoverGradient: 'from-blue-600 to-cyan-700'
    },
    {
      id: 'view-reports',
      title: 'View',
      subtitle: 'Reports',
      description: 'Access detailed analytics',
      icon: Eye,
      gradient: 'from-purple-500 to-indigo-600',
      hoverGradient: 'from-purple-600 to-indigo-700'
    },
    {
      id: 'export-data',
      title: 'Export',
      subtitle: 'Data & Reports',
      description: 'Download your data',
      icon: Download,
      gradient: 'from-orange-500 to-red-600',
      hoverGradient: 'from-orange-600 to-red-700'
    }
  ];

  const handleActionClick = (actionId) => {
    if (onActionClick) {
      onActionClick(actionId);
    }
    // Default action handling
    switch (actionId) {
      case 'create-group':
        console.log('Navigate to create group session');
        break;
      case 'create-selection':
        console.log('Navigate to create selection session');
        break;
      case 'view-reports':
        console.log('Navigate to reports page');
        break;
      case 'export-data':
        console.log('Navigate to export center');
        break;
      default:
        break;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.2 }}
      className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"
    >
      {actions.map((action, index) => {
        const Icon = action.icon;
        return (
          <motion.div
            key={action.id}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            whileHover={{ 
              scale: 1.05, 
              y: -5,
              transition: { duration: 0.2 }
            }}
            whileTap={{ scale: 0.95 }}
            onClick={() => handleActionClick(action.id)}
            className={`bg-gradient-to-br ${action.gradient} hover:bg-gradient-to-br hover:${action.hoverGradient} rounded-2xl p-6 text-white cursor-pointer shadow-lg hover:shadow-xl transition-all duration-300 relative overflow-hidden group`}
          >
            {/* Background decoration */}
            <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            
            {/* Content */}
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-4">
                <div className="bg-white/20 backdrop-blur-sm p-3 rounded-xl group-hover:bg-white/30 transition-all duration-300">
                  <Icon className="w-6 h-6 group-hover:scale-110 transition-transform duration-300" />
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold group-hover:scale-105 transition-transform duration-300">
                    {action.title}
                  </div>
                  <div className="text-white/80 text-sm group-hover:text-white transition-colors duration-300">
                    {action.subtitle}
                  </div>
                </div>
              </div>
              
              <div className="text-white/90 group-hover:text-white transition-colors duration-300">
                {action.description}
              </div>

              {/* Animated arrow indicator */}
              <motion.div
                className="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100"
                initial={{ x: -10 }}
                whileHover={{ x: 0 }}
                transition={{ duration: 0.2 }}
              >
                <div className="w-6 h-6 border-2 border-white/50 rounded-full flex items-center justify-center">
                  <svg 
                    className="w-3 h-3" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path 
                      strokeLinecap="round" 
                      strokeLinejoin="round" 
                      strokeWidth={2} 
                      d="M9 5l7 7-7 7" 
                    />
                  </svg>
                </div>
              </motion.div>
            </div>
          </motion.div>
        );
      })}
    </motion.div>
  );
};

export default QuickActions;
