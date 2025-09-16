import React from "react";

const Footer = () => {
  return (
    <footer className="bg-blue-50 text-gray-700 py-4 text-center">
      <p className="text-sm">&copy; {new Date().getFullYear()} Workforce App. All rights reserved.</p>
    </footer>
  );
};

export default Footer;
