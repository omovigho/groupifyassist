import React from 'react';
import { motion } from 'framer-motion';

export const ParticleField = () => {
  const particles = Array.from({ length: 50 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 3 + 1,
    duration: Math.random() * 20 + 10,
    delay: Math.random() * 5,
  }));

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          className="absolute bg-blue-400/20 rounded-full"
          style={{
            left: `${particle.x}%`,
            top: `${particle.y}%`,
            width: `${particle.size}px`,
            height: `${particle.size}px`,
          }}
          animate={{
            y: [0, -30, 0],
            opacity: [0.2, 0.8, 0.2],
            scale: [0.5, 1, 0.5],
          }}
          transition={{
            duration: particle.duration,
            delay: particle.delay,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  );
};

export const WaveEffect = () => {
  return (
    <div className="absolute bottom-0 left-0 w-full overflow-hidden pointer-events-none">
      <svg
        className="relative block w-full h-32"
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
        <motion.path
          d="M0,60 C150,120 350,0 600,60 C850,120 1050,0 1200,60 V120 H0 V60 Z"
          fill="url(#waveGradient)"
          animate={{
            d: [
              "M0,60 C150,120 350,0 600,60 C850,120 1050,0 1200,60 V120 H0 V60 Z",
              "M0,80 C150,40 350,100 600,80 C850,60 1050,120 1200,80 V120 H0 V80 Z",
              "M0,60 C150,120 350,0 600,60 C850,120 1050,0 1200,60 V120 H0 V60 Z",
            ],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      </svg>
    </div>
  );
};
