import React, { useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Checkbox } from '../components/ui/checkbox';
import { toast } from 'sonner';
import { Hexagon, Shield } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Login = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    totp_code: '',
  });
  const [loading, setLoading] = useState(false);
  const [requires2FA, setRequires2FA] = useState(false);
  const [tempUserId, setTempUserId] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API}/auth/login`, {
        username: formData.username,
        password: formData.password,
        totp_code: formData.totp_code || null,
      });

      if (response.data.requires_2fa) {
        setRequires2FA(true);
        setTempUserId(response.data.user.id);
        toast.info('Please enter your 2FA code');
      } else {
        toast.success('Login successful!');
        onLogin(response.data.access_token, response.data.user);
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 hexagon-bg">
      <Card className="w-full max-w-md border-2" data-testid="login-card">
        <CardHeader className="space-y-1 text-center">
          <div className="flex justify-center mb-4">
            <Hexagon className="h-16 w-16 text-primary" fill="currentColor" />
          </div>
          <CardTitle className="text-3xl font-bold" style={{ fontFamily: 'Work Sans, sans-serif' }}>
            BeeHive
          </CardTitle>
          <CardDescription>Website Manager - Sign in to your account</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {!requires2FA ? (
              <>
                <div className="space-y-2">
                  <Label htmlFor="username">Username</Label>
                  <Input
                    data-testid="login-username-input"
                    id="username"
                    type="text"
                    placeholder="Enter your username"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    data-testid="login-password-input"
                    id="password"
                    type="password"
                    placeholder="Enter your password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    required
                  />
                </div>
              </>
            ) : (
              <div className="space-y-2">
                <Label htmlFor="totp_code" className="flex items-center gap-2">
                  <Shield className="h-4 w-4 text-primary" />
                  2FA Code
                </Label>
                <Input
                  data-testid="login-2fa-input"
                  id="totp_code"
                  type="text"
                  placeholder="Enter 6-digit code"
                  value={formData.totp_code}
                  onChange={(e) => setFormData({ ...formData, totp_code: e.target.value })}
                  maxLength={6}
                  required
                />
              </div>
            )}
            <Button
              data-testid="login-submit-button"
              type="submit"
              className="w-full"
              disabled={loading}
            >
              {loading ? 'Signing in...' : requires2FA ? 'Verify' : 'Sign In'}
            </Button>
            {requires2FA && (
              <Button
                data-testid="login-back-button"
                type="button"
                variant="outline"
                className="w-full"
                onClick={() => {
                  setRequires2FA(false);
                  setFormData({ ...formData, totp_code: '' });
                }}
              >
                Back to Login
              </Button>
            )}
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default Login;
