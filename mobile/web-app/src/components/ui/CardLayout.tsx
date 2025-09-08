import React from 'react';

interface CardLayoutProps {
  title: string;
  description?: string;
  children: React.ReactNode;
}

const CardLayout: React.FC<CardLayoutProps> = ({ title, description, children }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-700 mb-2">{title}</h3>
      {description && <p className="text-sm text-gray-500 mb-4">{description}</p>}
      <div>{children}</div>
    </div>
  );
};

export default CardLayout;
