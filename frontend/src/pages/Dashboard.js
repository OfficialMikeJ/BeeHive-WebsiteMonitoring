import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { useTheme } from '../components/ThemeProvider';
import { Hexagon, Moon, Sun, LogOut, Home, Globe, Users, Settings, Activity } from 'lucide-react';
import { toast } from 'sonner';
import OverviewPage from './OverviewPage';
import WebsitesPage from './WebsitesPage';
import UsersPage from './UsersPage';
import SettingsPage from './SettingsPage';
import WelcomePopup from '../components/WelcomePopup';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = ({ user, onLogout }) => {
  const { theme, setTheme } = useTheme();
  const navigate = useNavigate();
  const [showWelcome, setShowWelcome] = useState(false);
  const [weeklyStats, setWeeklyStats] = useState(null);

  useEffect(() => {
    // Show welcome popup on first load
    const lastShown = localStorage.getItem('lastWelcomeShown');
    const today = new Date().toDateString();
    
    if (lastShown !== today) {
      fetchWeeklyStats();
      setTimeout(() => setShowWelcome(true), 500);
      localStorage.setItem('lastWelcomeShown', today);
    }
  }, []);

  const fetchWeeklyStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/stats/weekly`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setWeeklyStats(response.data);
    } catch (error) {
      console.error('Error fetching weekly stats:', error);
    }
  };

  const handleLogout = () => {
    toast.success('Logged out successfully');
    onLogout();
    navigate('/login');
  };

  const navigation = [
    { name: 'Overview', path: '/dashboard', icon: Home },
    { name: 'Websites', path: '/dashboard/websites', icon: Globe },
    { name: 'Users', path: '/dashboard/users', icon: Users, adminOnly: true },
    { name: 'Settings', path: '/dashboard/settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <Hexagon className="h-8 w-8 text-primary" fill="currentColor" data-testid="dashboard-logo" />
              <div>
                <h1 className="text-xl font-bold" style={{ fontFamily: 'Work Sans, sans-serif' }}>
                  BeeHive
                </h1>
                <p className="text-xs text-muted-foreground">Website Manager</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Button
                data-testid="theme-toggle-button"
                variant="ghost"
                size="icon"
                onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              >
                {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
              </Button>
              <div className="text-sm text-right hidden sm:block">
                <p className="font-medium">{user?.username}</p>
                <p className="text-xs text-muted-foreground capitalize">{user?.role}</p>
              </div>
              <Button
                data-testid="logout-button"
                variant="outline"
                size="sm"
                onClick={handleLogout}
              >
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 min-h-[calc(100vh-4rem)] border-r border-border bg-card hidden md:block">
          <nav className="p-4 space-y-2">
            {navigation.map((item) => {
              if (item.adminOnly && user?.role !== 'admin') return null;
              
              const Icon = item.icon;
              return (
                <Link key={item.name} to={item.path}>
                  <Button
                    data-testid={`nav-${item.name.toLowerCase()}-button`}
                    variant="ghost"
                    className="w-full justify-start"
                  >
                    <Icon className="h-5 w-5 mr-3" />
                    {item.name}
                  </Button>
                </Link>
              );
            })}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6 bg-background">
          <Routes>
            <Route path="/" element={<OverviewPage user={user} />} />
            <Route path="/websites" element={<WebsitesPage user={user} />} />
            <Route path="/users" element={<UsersPage user={user} />} />
            <Route path="/settings" element={<SettingsPage user={user} />} />
          </Routes>
        </main>
      </div>

      {/* Welcome Popup */}
      {showWelcome && weeklyStats && (
        <WelcomePopup
          stats={weeklyStats}
          onClose={() => setShowWelcome(false)}
          username={user?.username}
        />
      )}
    </div>
  );
};

export default Dashboard;
