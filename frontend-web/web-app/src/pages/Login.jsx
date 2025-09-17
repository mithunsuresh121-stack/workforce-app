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
          <p className="mt-2 text-gray-600">Sign in to your account</p>
        </div>
        {error && (
          <div className="mb-6 text-red-600 text-center font-semibold">{error}</div>
        )}
        <form onSubmit={handleSubmit} className="space-y-6">
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
              autoComplete="email"
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
                autoComplete="current-password"
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
            Sign In
          </button>
        </form>
        <p className="mt-6 text-center text-gray-600">
          Don't have an account?{' '}
          <a href="/signup" className={`${theme.components.link} hover:underline font-semibold`}>
            Sign Up
          </a>
        </p>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default Login;
