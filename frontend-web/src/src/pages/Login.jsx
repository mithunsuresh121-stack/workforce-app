import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { theme } from '../theme.js';
import { useNavigate } from 'react-router-dom';
import Footer from '../components/Footer';
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';

// ⚠️ LOCKED DESIGN: Do not override styles directly in this component.
// All styles must be sourced from the centralized theme.ts file.
// Extend theme.ts if new styles are needed.

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    const result = await login(email, password);
    if (result.success) {
      navigate('/dashboard');
    } else {
      setError('Invalid email or password');
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-surface">
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="bg-surface rounded-linear border border-border shadow-linear w-full max-w-md p-8">
          <div className="mb-8 text-center">
            <div className="w-16 h-16 bg-accent-500 rounded-linear mx-auto mb-4 flex items-center justify-center">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold text-neutral-900 mb-2">
              Welcome back
            </h2>
            <p className="text-neutral-600">Sign in to your account</p>
          </div>
          {error && (
            <div className="mb-6 bg-danger-50 border border-danger-200 rounded-linear p-4">
              <p className="text-danger-700 text-center font-medium">{error}</p>
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-6">
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
                autoComplete="email"
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
                  autoComplete="current-password"
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
              Sign In
            </button>
          </form>
          <p className="mt-6 text-center text-neutral-600">
            Don't have an account?{' '}
            <a href="/signup" className="text-accent-600 hover:text-accent-700 font-medium transition-colors duration-200">
              Sign Up
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
