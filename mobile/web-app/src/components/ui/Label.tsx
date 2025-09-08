import React, { LabelHTMLAttributes } from 'react';

const Label: React.FC<LabelHTMLAttributes<HTMLLabelElement>> = ({ className = '', ...props }) => {
  return (
    <label
      className={`block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 ${className}`}
      {...props}
    />
  );
};

export default Label;
