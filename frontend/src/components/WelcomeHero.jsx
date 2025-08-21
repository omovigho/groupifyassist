import { motion } from 'framer-motion';
import { 
  Users,
  Globe,
  Award,
  Zap,
  Clock,
  MapPin
} from 'lucide-react';

const WelcomeHero = ({ user, dashboardData }) => {
  const getTimeBasedGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const userName = user?.full_name || user?.email?.split('@')[0] || 'User';
  const userCountry = user?.country || 'Global';

  const highlights = [
    {
      icon: Globe,
      text: 'Global Reach',
      color: 'text-blue-200'
    },
    {
      icon: Award,
      text: 'Trusted Platform',
      color: 'text-blue-200'
    },
    {
      icon: Zap,
      text: 'Real-time Analytics',
      color: 'text-blue-200'
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
      className="relative overflow-hidden"
    >
      <div className="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 rounded-3xl p-8 text-white relative">
        {/* Background Pattern */}
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-transparent"></div>
          <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-white/10 to-transparent rounded-full -mr-32 -mt-32"></div>
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-gradient-to-tr from-indigo-800/30 to-transparent rounded-full -ml-24 -mb-24"></div>
        </div>

        {/* Content */}
        <div className="relative z-10">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              {/* Greeting */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
              >
                <p className="text-blue-100 text-lg mb-2">
                  {getTimeBasedGreeting()}! 👋
                </p>
                <h2 className="text-3xl lg:text-4xl font-bold mb-2">
                  Welcome, {userName}
                </h2>
                <div className="flex items-center text-blue-100 mb-4">
                  <MapPin className="w-4 h-4 mr-2" />
                  <span>from {userCountry}</span>
                </div>
              </motion.div>

              {/* Stats */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.4 }}
                className="flex flex-wrap items-center gap-6 mb-6"
              >
                <div className="flex items-center">
                  <Users className="w-5 h-5 mr-2 text-blue-200" />
                  <span className="text-blue-100">
                    <span className="font-semibold text-white">
                      {dashboardData?.active_sessions || 0}
                    </span> Active Sessions
                  </span>
                </div>
                <div className="flex items-center">
                  <Clock className="w-5 h-5 mr-2 text-blue-200" />
                  <span className="text-blue-100">
                    <span className="font-semibold text-white">
                      {dashboardData?.total_participants || 0}
                    </span> Total Participants
                  </span>
                </div>
              </motion.div>

              {/* Highlights */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.6 }}
                className="flex flex-wrap items-center gap-6"
              >
                {highlights.map((highlight, index) => {
                  const Icon = highlight.icon;
                  return (
                    <motion.div
                      key={highlight.text}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.4, delay: 0.8 + index * 0.1 }}
                      className="flex items-center group cursor-pointer"
                    >
                      <div className="bg-white/10 p-2 rounded-lg mr-3 group-hover:bg-white/20 transition-all duration-300">
                        <Icon className={`w-4 h-4 ${highlight.color} group-hover:scale-110 transition-transform duration-300`} />
                      </div>
                      <span className="text-blue-100 group-hover:text-white transition-colors duration-300">
                        {highlight.text}
                      </span>
                    </motion.div>
                  );
                })}
              </motion.div>
            </div>

            {/* Animated Icon */}
            <div className="hidden lg:block ml-8">
              <motion.div
                animate={{ 
                  rotate: [0, 5, -5, 0],
                  scale: [1, 1.05, 1]
                }}
                transition={{ 
                  duration: 4,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
                className="relative"
              >
                <div className="w-32 h-32 bg-white/10 rounded-full flex items-center justify-center backdrop-blur-sm border border-white/20">
                  <Users className="w-16 h-16 text-white" />
                </div>
                
                {/* Floating dots */}
                <motion.div
                  animate={{ y: [0, -8, 0] }}
                  transition={{ duration: 2, repeat: Infinity, delay: 0 }}
                  className="absolute -top-2 -right-2 w-4 h-4 bg-white/30 rounded-full"
                />
                <motion.div
                  animate={{ y: [0, -8, 0] }}
                  transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
                  className="absolute -bottom-2 -left-2 w-3 h-3 bg-blue-300/40 rounded-full"
                />
                <motion.div
                  animate={{ y: [0, -8, 0] }}
                  transition={{ duration: 2, repeat: Infinity, delay: 1 }}
                  className="absolute top-8 -left-6 w-2 h-2 bg-indigo-300/50 rounded-full"
                />
              </motion.div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default WelcomeHero;
