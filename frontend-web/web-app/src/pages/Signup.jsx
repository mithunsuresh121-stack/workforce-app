import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { theme } from '../theme';
import Footer from '../components/Footer';
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';

const Signup = () => {
  const { signup } = useAuth();
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const result = await signup(email, password, fullName);
      if (!result.success) {
        setError(result.error);
      }
    } catch (err) {
      setError('Signup failed');
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <div className="flex-1 flex items-center justify-center bg-gradient-to-r from-blue-500 to-indigo-600">
        <div className={`${theme.components.card} w-full max-w-md border border-gray-200`}>
          <div className="mb-8 text-center">
            <img
              src="/logo192.png"
              alt="Workforce App Logo"
              className="mx-auto mb-4 w-20 h-20 rounded-full shadow-md"
            />
            <h2 className={`${theme.typography.h1} tracking-wide`}>
              Workforce App
            </h2>
            <p className="mt-2 text-gray-600">Create your account</p>
          </div>
          {error && (
            <div className="mb-6 text-red-600 text-center font-semibold">{error}</div>
          )}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="fullName" className="block text-gray-700 font-semibold mb-2">
                Full Name
              </label>
              <input
                id="fullName"
                type="text"
                className={`${theme.components.input} px-5 py-3 focus:ring-4 focus:ring-indigo-400`}
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
                placeholder="Your full name"
              />
            </div>
            <div>
              <label htmlFor="email" className="block text-gray-700 font-semibold mb-2">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                className={`${theme.components.input} px-5 py-3 focus:ring-4 focus:ring-indigo-400`}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="you@example.com"
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-gray-700 font-semibold mb-2">
                Password
              </label>
              <div className={theme.components.passwordInputWrapper}>
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  className={`${theme.components.input} px-5 py-3 pr-10 focus:ring-4 focus:ring-indigo-400`}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700 focus:outline-none"
                >
                  {showPassword ? <EyeSlashIcon className="h-5 w-5" /> : <EyeIcon className="h-5 w-5" />}
                </button>
              </div>
            </div>
            <button
              type="submit"
              className={`${theme.components.button} ${theme.components.buttonPrimary} w-full py-3 shadow-lg`}
            >
              Sign Up
            </button>
          </form>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default Signup;
