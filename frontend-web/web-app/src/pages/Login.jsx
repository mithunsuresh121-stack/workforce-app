import React, { useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardBody, Input, Button, Typography } from '@material-tailwind/react';
import { AuthContext } from '../context/AuthContext';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const { login } = useContext(AuthContext); // Use AuthContext for login

  useEffect(() => {
    console.log("Login mounted");
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Use AuthContext login function
    const success = login(email, password);
    if (success) {
      navigate('/dashboard');
    } else {
      alert('Invalid credentials. Try admin/password');
    }
  };

  return (
    <div className="flex items-center justify-center h-screen bg-gray-50">
      <Card className="w-96 p-6">
        <Typography variant="h4" color="blue-gray" className="mb-6 text-center">
          Login
        </Typography>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Input
            type="email"
            label="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <Input
            type="password"
            label="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <Button type="submit" color="blue" className="mt-4">
            Sign In
          </Button>
        </form>
      </Card>
    </div>
  );
};

export default Login;
