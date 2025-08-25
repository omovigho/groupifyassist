import React from 'react';

export const Button = ({ 
  variant = 'default', 
  size = 'default', 
  className = '', 
  children, 
  ...props 
}) => {
  const baseClasses = "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50";
  
  const variantClasses = {
    default: "bg-blue-600 text-white hover:bg-blue-700",
    ghost: "hover:bg-white/10 text-white/90 hover:text-white",
    gradient: "bg-gradient-to-r from-blue-600 via-purple-600 to-cyan-500 text-white font-semibold hover:from-blue-700 hover:via-purple-700 hover:to-cyan-600 transition-all duration-300 shadow-lg hover:shadow-xl",
    outline: "border border-white/20 bg-transparent text-white hover:bg-white/10",
    secondary: "bg-gray-600 text-white hover:bg-gray-700",
  };

  const sizeClasses = {
    default: "h-10 px-4 py-2",
    sm: "h-9 rounded-md px-3",
    lg: "h-11 rounded-md px-8",
    icon: "h-10 w-10",
  };

  const combinedClassName = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`;

  return (
    <button className={combinedClassName} {...props}>
      {children}
    </button>
  );
};
