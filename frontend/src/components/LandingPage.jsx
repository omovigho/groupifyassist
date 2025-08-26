import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/simple-button';
import { Input } from '@/components/ui/simple-input';
import { Users, ArrowRight, LogIn, UserPlus } from '@/components/ui/simple-icons';
import { AnimatedBackground } from '@/components/AnimatedBackground';
import { ParticleField, WaveEffect } from '@/components/AnimatedEffects';

const LandingPage = () => {
  const [accessCode, setAccessCode] = useState('');

  const handleJoinGroup = (e) => {
    e.preventDefault();
    if (accessCode.trim()) {
      alert(`Joining group with code: ${accessCode}`);
      // TODO: Implement actual join logic
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        duration: 0.8,
        staggerChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { y: 50, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.6,
        ease: [0.6, -0.05, 0.01, 0.99]
      }
    }
  };

  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden">
      {/* Animated Background */}
      <AnimatedBackground />
      
      {/* Additional animated effects */}
      <ParticleField />
      <WaveEffect />

      {/* Navigation */}
      <motion.header 
        className="relative z-10 p-6"
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <nav className="max-w-7xl mx-auto flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl shadow-lg">
              <Users className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-gradient">
              GroupifyAssist
            </span>
          </div>

          {/* Navigation Buttons */}
          <div className="hidden md:flex items-center space-x-4">
            <Button 
              variant="ghost" 
              className="text-white/90 hover:text-white hover:bg-white/10 border border-white/20"
            >
              <LogIn className="w-4 h-4 mr-2" />
              Login
            </Button>
            <Button 
              variant="gradient"
              className="shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300"
            >
              <UserPlus className="w-4 h-4 mr-2" />
              Sign Up
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <Button 
            variant="ghost" 
            size="icon"
            className="md:hidden text-white/90 hover:text-white hover:bg-white/10"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </Button>
        </nav>
      </motion.header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center px-6 relative z-10">
        <motion.div
          className="max-w-4xl mx-auto text-center"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Hero Title */}
          <motion.div variants={itemVariants}>
            <h1 className="text-5xl md:text-7xl font-extrabold mb-6 leading-tight">
              Welcome to{' '}
              <span className="text-gradient">
                GroupifyAssist
              </span>
            </h1>
          </motion.div>

          {/* Subtitle */}
          <motion.p 
            className="text-xl md:text-2xl text-gray-300 mb-12 max-w-3xl mx-auto leading-relaxed"
            variants={itemVariants}
          >
            Effortless Grouping & Smart Selection, Anytime, Anywhere.
          </motion.p>

          {/* Access Code Form */}
          <motion.div variants={itemVariants}>
            <form 
              onSubmit={handleJoinGroup}
              className="max-w-md mx-auto mb-6"
            >
              <div className="flex flex-col sm:flex-row gap-3">
                <Input
                  type="text"
                  placeholder="Enter Access Code..."
                  value={accessCode}
                  onChange={(e) => setAccessCode(e.target.value)}
                  className="flex-1 h-14 text-lg bg-white/10 border-white/20 text-white placeholder:text-gray-400 backdrop-blur-sm"
                  maxLength={64}
                  required
                />
                <Button 
                  type="submit"
                  variant="gradient"
                  className="h-14 px-8 text-lg font-semibold shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-300"
                >
                  Join Group
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </div>
            </form>

            <motion.p 
              className="text-sm text-gray-400"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1, duration: 0.5 }}
            >
              Have a code from an organizer? Paste it above and jump right in.
            </motion.p>
          </motion.div>

          {/* Feature highlights */}
          <motion.div 
            className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto"
            variants={containerVariants}
          >
            {[
              { title: "Smart Grouping", desc: "AI-powered team formation" },
              { title: "Fair Selection", desc: "Unbiased participant picking" },
              { title: "Real-time Updates", desc: "Live session monitoring" }
            ].map((feature, index) => (
              <motion.div
                key={index}
                variants={itemVariants}
                className="p-6 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 hover:bg-white/10 transition-all duration-300"
              >
                <h3 className="text-lg font-semibold text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-400 text-sm">
                  {feature.desc}
                </p>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>
      </main>

      {/* Footer */}
      <motion.footer 
        className="relative z-10 p-6 mt-auto"
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.5 }}
      >
        <div className="max-w-7xl mx-auto text-center">
          <p className="text-gray-400 text-sm">
            © 2025 GroupifyAssist. All rights reserved.
          </p>
        </div>
      </motion.footer>

      {/* Mobile Menu (when expanded) */}
      <div className="fixed inset-0 z-50 hidden" id="mobile-menu">
        <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />
        <div className="absolute right-0 top-0 h-full w-80 max-w-[85%] bg-navy-900/95 backdrop-blur-md p-6">
          <div className="flex flex-col space-y-4">
            <Button variant="ghost" className="justify-start text-white">
              <LogIn className="w-4 h-4 mr-2" />
              Login
            </Button>
            <Button variant="gradient">
              <UserPlus className="w-4 h-4 mr-2" />
              Sign Up
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
