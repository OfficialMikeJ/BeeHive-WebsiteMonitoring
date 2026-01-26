import React, { useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { toast } from 'sonner';
import { Shield, Lock, Key } from 'lucide-react';
import { QRCodeCanvas } from 'qrcode.react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SettingsPage = ({ user }) => {
  const [passwordData, setPasswordData] = useState({
    old_password: '',
    new_password: '',
    confirm_password: '',
  });
  const [twoFASetup, setTwoFASetup] = useState(null);
  const [twoFACode, setTwoFACode] = useState('');
  const [loading, setLoading] = useState(false);

  const handlePasswordChange = async (e) => {
    e.preventDefault();

    if (passwordData.new_password !== passwordData.confirm_password) {
      toast.error('Passwords do not match');
      return;
    }

    if (passwordData.new_password.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API}/auth/change-password`,
        {
          old_password: passwordData.old_password,
          new_password: passwordData.new_password,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('Password changed successfully');
      setPasswordData({ old_password: '', new_password: '', confirm_password: '' });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  const handleSetup2FA = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/auth/2fa/setup`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setTwoFASetup(response.data);
      toast.success('2FA setup initiated');
    } catch (error) {
      toast.error('Failed to setup 2FA');
    } finally {
      setLoading(false);
    }
  };

  const handleEnable2FA = async () => {
    if (!twoFACode || twoFACode.length !== 6) {
      toast.error('Please enter a valid 6-digit code');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API}/auth/2fa/enable`,
        { totp_code: twoFACode },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('2FA enabled successfully');
      setTwoFASetup(null);
      setTwoFACode('');
      window.location.reload();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to enable 2FA');
    } finally {
      setLoading(false);
    }
  };

  const handleDisable2FA = async () => {
    if (!window.confirm('Are you sure you want to disable 2FA?')) return;

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/auth/2fa/disable`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      toast.success('2FA disabled successfully');
      window.location.reload();
    } catch (error) {
      toast.error('Failed to disable 2FA');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6" data-testid="settings-page">
      <div>
        <h2 className="text-3xl font-bold mb-2" style={{ fontFamily: 'Work Sans, sans-serif' }}>
          Settings
        </h2>
        <p className="text-muted-foreground">Manage your account settings and security</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Change Password */}
        <Card data-testid="change-password-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lock className="h-5 w-5" />
              Change Password
            </CardTitle>
            <CardDescription>Update your account password</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handlePasswordChange} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="old_password">Current Password</Label>
                <Input
                  data-testid="old-password-input"
                  id="old_password"
                  type="password"
                  value={passwordData.old_password}
                  onChange={(e) =>
                    setPasswordData({ ...passwordData, old_password: e.target.value })
                  }
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="new_password">New Password</Label>
                <Input
                  data-testid="new-password-input"
                  id="new_password"
                  type="password"
                  value={passwordData.new_password}
                  onChange={(e) =>
                    setPasswordData({ ...passwordData, new_password: e.target.value })
                  }
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirm_password">Confirm New Password</Label>
                <Input
                  data-testid="confirm-password-input"
                  id="confirm_password"
                  type="password"
                  value={passwordData.confirm_password}
                  onChange={(e) =>
                    setPasswordData({ ...passwordData, confirm_password: e.target.value })
                  }
                  required
                />
              </div>
              <Button
                data-testid="change-password-button"
                type="submit"
                className="w-full"
                disabled={loading}
              >
                {loading ? 'Changing...' : 'Change Password'}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* 2FA Settings */}
        <Card data-testid="2fa-settings-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Two-Factor Authentication
            </CardTitle>
            <CardDescription>
              {user?.twofa_enabled
                ? '2FA is currently enabled'
                : 'Add an extra layer of security'}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {!user?.twofa_enabled && !twoFASetup && (
              <Button
                data-testid="setup-2fa-button"
                onClick={handleSetup2FA}
                className="w-full"
                disabled={loading}
              >
                <Key className="h-4 w-4 mr-2" />
                Setup 2FA
              </Button>
            )}

            {twoFASetup && (
              <div className="space-y-4">
                <div className="bg-card border rounded-lg p-4 text-center">
                  <p className="text-sm text-muted-foreground mb-3">
                    Scan this QR code with your authenticator app
                  </p>
                  <div className="flex justify-center mb-3">
                    <QRCodeCanvas value={twoFASetup.uri} size={200} />
                  </div>
                  <p className="text-xs text-muted-foreground mb-2">Or enter this secret manually:</p>
                  <code className="text-xs bg-muted px-2 py-1 rounded">{twoFASetup.secret}</code>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="totp_code">Enter 6-digit code to verify</Label>
                  <Input
                    data-testid="2fa-code-input"
                    id="totp_code"
                    type="text"
                    maxLength={6}
                    placeholder="000000"
                    value={twoFACode}
                    onChange={(e) => setTwoFACode(e.target.value)}
                  />
                </div>
                <Button
                  data-testid="enable-2fa-button"
                  onClick={handleEnable2FA}
                  className="w-full"
                  disabled={loading}
                >
                  Enable 2FA
                </Button>
              </div>
            )}

            {user?.twofa_enabled && (
              <div className="space-y-4">
                <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
                  <p className="text-sm text-green-500 font-medium">✓ 2FA is active</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Your account is protected with two-factor authentication
                  </p>
                </div>
                <Button
                  data-testid="disable-2fa-button"
                  onClick={handleDisable2FA}
                  variant="destructive"
                  className="w-full"
                  disabled={loading}
                >
                  Disable 2FA
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Account Info */}
      <Card data-testid="account-info-card">
        <CardHeader>
          <CardTitle>Account Information</CardTitle>
          <CardDescription>Your account details</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label className="text-muted-foreground">Username</Label>
              <p className="font-medium mt-1">{user?.username}</p>
            </div>
            <div>
              <Label className="text-muted-foreground">Email</Label>
              <p className="font-medium mt-1">{user?.email}</p>
            </div>
            <div>
              <Label className="text-muted-foreground">Role</Label>
              <p className="font-medium mt-1 capitalize">{user?.role}</p>
            </div>
            <div>
              <Label className="text-muted-foreground">2FA Status</Label>
              <p className={`font-medium mt-1 ${user?.twofa_enabled ? 'text-green-500' : ''}`}>
                {user?.twofa_enabled ? 'Enabled' : 'Disabled'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SettingsPage;
