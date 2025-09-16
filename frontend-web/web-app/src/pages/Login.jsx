import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import Footer from "../components/Footer";

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth(); // useAuth hook for authentication
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false);

  // Handle login form submission
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    const result = await login(email, password);
    setLoading(false);
    if (result.success) {
      navigate("/dashboard"); // Redirect to dashboard on successful login
    } else {
      setError(result.error || "Invalid credentials");
    }
  };

  // Handle sign up form submission (dummy implementation)
  const handleSignUp = async (e) => {
    e.preventDefault();
    // Implement sign up logic here or navigate to sign up page
    alert("Sign up feature is not implemented yet.");
  };

  return (
    <div className="min-h-screen flex flex-col justify-between bg-gradient-to-r from-blue-50 to-gray-100 p-4">
      <div className="flex items-center justify-center flex-grow">
        {/* Card container */}
        <div className="w-full max-w-md bg-white rounded-lg shadow-lg overflow-hidden">
          {/* Card header */}
          <div className="bg-blue-600 text-center py-6 flex flex-col items-center">
            <img
              src="/logo192.png"
              alt="App Logo"
              className="mb-2 w-20 h-20 object-contain"
            />
            <h1 className="text-2xl font-bold text-white">
              Workforce App
            </h1>
          </div>

          {/* Card body */}
          <div className="p-6 flex flex-col gap-4">
            {error && (
              <p className="text-red-600 text-center text-sm">{error}</p>
            )}

            {!isSignUp ? (
              <form onSubmit={handleLogin}>
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

                <div className="relative">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Password
                  </label>
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 pr-10"
                    autoComplete="current-password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-500 hover:text-gray-700 focus:outline-none"
                    tabIndex={-1}
                  >
                    {showPassword ? (
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M10 3C5 3 1.73 7.11 1 10c.73 2.89 4 7 9 7s8.27-4.11 9-7c-.73-2.89-4-7-9-7zM10 15a5 5 0 110-10 5 5 0 010 10z" />
                        <path d="M10 7a3 3 0 100 6 3 3 0 000-6z" />
                      </svg>
                    ) : (
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M3.707 3.293a1 1 0 00-1.414 1.414l1.528 1.528A9.953 9.953 0 001 10c.73 2.89 4 7 9 7a9.96 9.96 0 005.657-1.828l1.528 1.528a1 1 0 001.414-1.414l-14-14zM10 13a3 3 0 01-3-3c0-.34.07-.66.19-.95l3.76 3.76A2.99 2.99 0 0110 13z" />
                      </svg>
                    )}
                  </button>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed mt-4"
                >
                  {loading ? "Logging in..." : "Login"}
                </button>
                <p className="mt-4 text-center text-sm text-gray-600">
                  Don't have an account?{" "}
                  <button
                    type="button"
                    className="text-blue-600 hover:underline"
                    onClick={() => setIsSignUp(true)}
                  >
                    Sign Up
                  </button>
                </p>
              </form>
            ) : (
              <form onSubmit={handleSignUp}>
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
                    autoComplete="new-password"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? "Signing up..." : "Sign Up"}
                </button>
                <p className="mt-4 text-center text-sm text-gray-600">
                  Already have an account?{" "}
                  <button
                    type="button"
                    className="text-green-600 hover:underline"
                    onClick={() => setIsSignUp(false)}
                  >
                    Login
                  </button>
                </p>
              </form>
            )}
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default Login;
