import React from 'react';

export const SimpleParticleField = () => {
  const particles = Array.from({ length: 30 }, (_, i) => ({
    id: i,
    left: Math.random() * 100,
    top: Math.random() * 100,
    size: Math.random() * 3 + 1,
    delay: Math.random() * 5,
  }));

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {particles.map((particle) => (
        <div
          key={particle.id}
          className="absolute bg-blue-400/20 rounded-full animate-pulse"
          style={{
            left: `${particle.left}%`,
            top: `${particle.top}%`,
            width: `${particle.size}px`,
            height: `${particle.size}px`,
            animationDelay: `${particle.delay}s`,
          }}
        />
      ))}
    </div>
  );
};

export const SimpleWaveEffect = () => {
  return (
    <div className="absolute bottom-0 left-0 w-full overflow-hidden pointer-events-none">
      <svg
        className="relative block w-full h-32 animate-pulse"
        viewBox="0 0 1200 120"
        preserveAspectRatio="none"
      >
        <defs>
          <linearGradient id="waveGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.3" />
            <stop offset="50%" stopColor="#8b5cf6" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.3" />
          </linearGradient>
        </defs>
        <path
          d="M0,60 C150,120 350,0 600,60 C850,120 1050,0 1200,60 V120 H0 V60 Z"
          fill="url(#waveGradient)"
        />
      </svg>
    </div>
  );
};
