import React from 'react';

const Skeleton: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div className={`bg-gray-200 dark:bg-gray-700 rounded-md ${className}`} />
  );
};

export default Skeleton;
