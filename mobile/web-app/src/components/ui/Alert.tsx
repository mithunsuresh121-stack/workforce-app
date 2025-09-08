import React, { ReactNode } from 'react';

interface AlertProps {
  variant?: 'default' | 'destructive';
  children: ReactNode;
  className?: string;
}

export const AlertTitle: React.FC<{ children: ReactNode }> = ({ children }) => (
  <h3 className="font-semibold leading-none tracking-tight">{children}</h3>
);

export const AlertDescription: React.FC<{ children: ReactNode }> = ({ children }) => (
  <div className="text-sm opacity-90">{children}</div>
);

const Alert: React.FC<AlertProps> = ({ variant = 'default', children, className = '' }) => {
  const baseClasses = 'rounded-md border p-4';
  const variantClasses =
    variant === 'destructive'
      ? 'bg-red-50 border-red-500 text-red-700'
      : 'bg-gray-50 border-gray-200 text-gray-700';

  return <div className={`${baseClasses} ${variantClasses} ${className}`}>{children}</div>;
};

export default Alert;
