import React from 'react';

const SimpleFloatingOrb = ({ 
  size, 
  color, 
  delay = 0, 
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
    <div
      className={`
        absolute rounded-full blur-xl animate-float
        ${sizeClasses[size]} 
        ${colorClasses[color]}
        ${className}
      `}
      style={{ animationDelay: `${delay}s` }}
    />
  );
};

export const SimpleAnimatedBackground = () => {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none">
      {/* Main gradient background */}
      <div className="absolute inset-0 hero-gradient" />
      
      {/* Floating orbs */}
      <SimpleFloatingOrb 
        size="lg" 
        color="blue" 
        delay={0} 
        className="top-1/4 left-1/4" 
      />
      <SimpleFloatingOrb 
        size="md" 
        color="purple" 
        delay={5} 
        className="top-3/4 right-1/4" 
      />
      <SimpleFloatingOrb 
        size="sm" 
        color="cyan" 
        delay={10} 
        className="top-1/2 left-3/4" 
      />
      <SimpleFloatingOrb 
        size="md" 
        color="indigo" 
        delay={15} 
        className="bottom-1/4 left-1/2" 
      />
      <SimpleFloatingOrb 
        size="sm" 
        color="blue" 
        delay={8} 
        className="top-1/3 right-1/3" 
      />

      {/* Subtle overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-navy-950/50 via-transparent to-navy-900/30" />
    </div>
  );
};
