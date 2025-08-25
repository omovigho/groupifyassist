import React from 'react';

export const Input = ({ className = '', ...props }) => {
  const baseClasses = "flex h-10 w-full rounded-md border border-white/20 bg-white/10 backdrop-blur-sm px-3 py-2 text-sm text-white placeholder:text-gray-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/50 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-200";
  
  const combinedClassName = `${baseClasses} ${className}`;

  return (
    <input className={combinedClassName} {...props} />
  );
};
