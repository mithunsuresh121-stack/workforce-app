import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { Card, CardHeader, CardBody, Typography, Input, Button } from '@material-tailwind/react';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Mock login for testing - replace with actual API call
      // const response = await axios.post('/api/login', { email, password });
      // login(response.data.user);

      // For now, mock user data
      const mockUser = { id: 1, name: 'John Doe', email, avatar: 'https://via.placeholder.com/40' };
      login(mockUser);
      navigate('/dashboard');
    } catch (error) {
      alert('Login failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader floated={false} className="h-28 m-0 grid place-items-center bg-blue-600">
          <Typography variant="h4" color="white">
            Sign In to Workforce App
          </Typography>
        </CardHeader>
        <CardBody>
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <Typography variant="small" color="blue-gray" className="mb-2 font-medium">
                Email
              </Typography>
              <Input
                type="email"
                size="lg"
                placeholder="name@mail.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div>
              <Typography variant="small" color="blue-gray" className="mb-2 font-medium">
                Password
              </Typography>
              <Input
                type="password"
                size="lg"
                placeholder="********"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <Button type="submit" className="w-full" size="lg">
              Sign In
            </Button>
          </form>
        </CardBody>
      </Card>
    </div>
  );
};

export default Login;
