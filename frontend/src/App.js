import React, { useState, useEffect } from 'react';
import '@/App.css';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import Login from './pages/Login';
import Setup from './pages/Setup';
import Dashboard from './pages/Dashboard';
import { ThemeProvider } from './components/ThemeProvider';
import { Toaster } from './components/ui/sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [setupComplete, setSetupComplete] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    checkSetup();
    checkAuth();
  }, []);

  const checkSetup = async () => {
    try {
      const response = await axios.get(`${API}/setup/status`);
      setSetupComplete(response.data.setup_complete);
    } catch (error) {
      console.error('Error checking setup:', error);
    }
  };

  const checkAuth = () => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    if (token && userData) {
      setIsAuthenticated(true);
      setUser(JSON.parse(userData));
    }
    setIsLoading(false);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <ThemeProvider defaultTheme="dark" storageKey="beehive-theme">
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route
              path="/setup"
              element={
                !setupComplete ? (
                  <Setup onSetupComplete={() => setSetupComplete(true)} />
                ) : (
                  <Navigate to="/login" replace />
                )
              }
            />
            <Route
              path="/login"
              element={
                !isAuthenticated ? (
                  <Login
                    onLogin={(token, userData) => {
                      localStorage.setItem('token', token);
                      localStorage.setItem('user', JSON.stringify(userData));
                      setIsAuthenticated(true);
                      setUser(userData);
                    }}
                  />
                ) : (
                  <Navigate to="/dashboard" replace />
                )
              }
            />
            <Route
              path="/dashboard/*"
              element={
                isAuthenticated ? (
                  <Dashboard
                    user={user}
                    onLogout={() => {
                      localStorage.removeItem('token');
                      localStorage.removeItem('user');
                      setIsAuthenticated(false);
                      setUser(null);
                    }}
                  />
                ) : (
                  <Navigate to="/login" replace />
                )
              }
            />
            <Route
              path="/"
              element={
                !setupComplete ? (
                  <Navigate to="/setup" replace />
                ) : isAuthenticated ? (
                  <Navigate to="/dashboard" replace />
                ) : (
                  <Navigate to="/login" replace />
                )
              }
            />
          </Routes>
        </BrowserRouter>
        <Toaster position="top-right" />
      </div>
    </ThemeProvider>
  );
}

export default App;
