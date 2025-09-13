import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth(); // useAuth hook for authentication
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  // Handle login form submission
  const handleLogin = (e) => {
    e.preventDefault();
    try {
      login(email, password);
      navigate("/dashboard"); // Redirect to dashboard on successful login
    } catch (err) {
      setError("Invalid credentials");
    }
  };

  return (
    // Full screen container with gradient background, centers the card
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-r from-blue-50 to-gray-100 p-4">
      {/* Login card using Tailwind classes */}
      <div className="w-full max-w-md bg-white rounded-lg shadow-lg overflow-hidden">
        {/* Card header with logo and app name */}
        <div className="bg-blue-600 text-center py-6 flex flex-col items-center">
          {/* Logo image - ensure logo192.png is in public folder */}
          <img
            src="/logo192.png"
            alt="App Logo"
            className="mb-2 w-20 h-20 object-contain"
          />
          {/* App name */}
          <h1 className="text-2xl font-bold text-white">
            Workforce App
          </h1>
        </div>

        {/* Card body containing the login form inputs and button */}
        <div className="p-6 flex flex-col gap-4">
          {/* Display error message if login fails */}
          {error && (
            <p className="text-red-600 text-center text-sm">
              {error}
            </p>
          )}

          {/* Email input field */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              autoComplete="email"
            />
          </div>

          {/* Password input field */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              autoComplete="current-password"
            />
          </div>

          {/* Login button */}
          <button
            onClick={handleLogin}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 mt-4"
          >
            Login
          </button>
        </div>
      </div>
    </div>
  );
};

export default Login;
