import React from 'react';
import { motion } from 'framer-motion';

const FloatingOrb = ({ 
  size, 
  color, 
  delay = 0, 
  duration = 20,
  className = '' 
}) => {
  const sizeClasses = {
    sm: 'w-32 h-32',
    md: 'w-48 h-48', 
    lg: 'w-64 h-64'
  };

  const colorClasses = {
    blue: 'bg-gradient-to-br from-blue-400/20 to-blue-600/10',
    purple: 'bg-gradient-to-br from-purple-400/20 to-purple-600/10',
    cyan: 'bg-gradient-to-br from-cyan-400/20 to-cyan-600/10',
    indigo: 'bg-gradient-to-br from-indigo-400/20 to-indigo-600/10',
  };

  return (
    <motion.div
      className={`
        absolute rounded-full blur-xl 
        ${sizeClasses[size]} 
        ${colorClasses[color]}
        ${className}
      `}
      animate={{
        x: [0, 100, -50, 0],
        y: [0, -100, 50, 0],
        scale: [1, 1.2, 0.8, 1],
        rotate: [0, 180, 360],
      }}
      transition={{
        duration,
        delay,
        repeat: Infinity,
        ease: "easeInOut"
      }}
    />
  );
};

export const AnimatedBackground = () => {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none">
      {/* Main gradient background */}
      <div className="absolute inset-0 hero-gradient" />
      
      {/* Floating orbs */}
      <FloatingOrb 
        size="lg" 
        color="blue" 
        delay={0} 
        duration={25}
        className="top-1/4 left-1/4" 
      />
      <FloatingOrb 
        size="md" 
        color="purple" 
        delay={5} 
        duration={30}
        className="top-3/4 right-1/4" 
      />
      <FloatingOrb 
        size="sm" 
        color="cyan" 
        delay={10} 
        duration={20}
        className="top-1/2 left-3/4" 
      />
      <FloatingOrb 
        size="md" 
        color="indigo" 
        delay={15} 
        duration={35}
        className="bottom-1/4 left-1/2" 
      />
      <FloatingOrb 
        size="sm" 
        color="blue" 
        delay={8} 
        duration={22}
        className="top-1/3 right-1/3" 
      />

      {/* Subtle overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-navy-950/50 via-transparent to-navy-900/30" />
    </div>
  );
};
