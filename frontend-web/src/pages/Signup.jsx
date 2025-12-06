import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { theme } from '../theme';
import Footer from '../components/Footer';
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';

const Signup = () => {
  const { signup, validationErrors, setValidationErrors } = useAuth();
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setValidationErrors([]);
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
    <div className="min-h-screen flex flex-col bg-surface">
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="bg-surface rounded-linear border border-border shadow-linear w-full max-w-md p-8">
          <div className="mb-8 text-center">
            <div className="w-16 h-16 bg-accent-500 rounded-linear mx-auto mb-4 flex items-center justify-center">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold text-neutral-900 mb-2">
              Create account
            </h2>
            <p className="text-neutral-600">Get started with your new account</p>
          </div>

          {validationErrors.length > 0 && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded-linear p-4">
              <p className="text-red-700 text-center font-medium">Please fix the following errors:</p>
              <ul className="mt-2 text-red-700">
                {validationErrors.map((msg, i) => (
                  <li key={i} className="text-sm">• {msg}</li>
                ))}
              </ul>
            </div>
          )}

          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded-linear p-4">
              <p className="text-red-700 text-center font-medium">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="fullName" className="block text-sm font-medium text-neutral-700 mb-2">
                Full Name
              </label>
              <input
                id="fullName"
                type="text"
                className="w-full px-4 py-3 border border-border rounded-linear bg-surface text-neutral-900 placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500 transition-colors duration-200"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
                placeholder="Your full name"
              />
            </div>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-neutral-700 mb-2">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                className="w-full px-4 py-3 border border-border rounded-linear bg-surface text-neutral-900 placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500 transition-colors duration-200"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="you@example.com"
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-neutral-700 mb-2">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  className="w-full px-4 py-3 pr-12 border border-border rounded-linear bg-surface text-neutral-900 placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500 transition-colors duration-200"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-neutral-400 hover:text-neutral-600 focus:outline-none transition-colors duration-200"
                >
                  {showPassword ? <EyeSlashIcon className="h-5 w-5" /> : <EyeIcon className="h-5 w-5" />}
                </button>
              </div>
            </div>
            <button
              type="submit"
              className="w-full bg-accent-500 hover:bg-accent-600 text-white font-medium py-3 px-4 rounded-linear transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:ring-offset-2"
            >
              Sign Up
            </button>
          </form>
          <p className="mt-6 text-center text-neutral-600">
            Already have an account?{' '}
            <a href="/login" className="text-accent-600 hover:text-accent-700 font-medium transition-colors duration-200">
              Sign In
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Signup;
