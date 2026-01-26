import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Activity, TrendingUp, Globe, Clock } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const OverviewPage = ({ user }) => {
  const [websites, setWebsites] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      const [websitesRes, statsRes] = await Promise.all([
        axios.get(`${API}/websites`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/stats/weekly`, { headers: { Authorization: `Bearer ${token}` } }),
      ]);
      setWebsites(websitesRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  const onlineWebsites = websites.filter((w) => w.status === 'online').length;
  const offlineWebsites = websites.filter((w) => w.status === 'offline').length;

  return (
    <div className="space-y-6" data-testid="overview-page">
      <div>
        <h2 className="text-3xl font-bold mb-2" style={{ fontFamily: 'Work Sans, sans-serif' }}>
          Overview
        </h2>
        <p className="text-muted-foreground">Monitor your websites at a glance</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card data-testid="total-websites-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Websites</CardTitle>
            <Globe className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{websites.length}</div>
            <p className="text-xs text-muted-foreground">of 10 maximum</p>
          </CardContent>
        </Card>

        <Card data-testid="online-websites-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Online</CardTitle>
            <Activity className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">{onlineWebsites}</div>
            <p className="text-xs text-muted-foreground">websites operational</p>
          </CardContent>
        </Card>

        <Card data-testid="offline-websites-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Offline</CardTitle>
            <Activity className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-500">{offlineWebsites}</div>
            <p className="text-xs text-muted-foreground">websites down</p>
          </CardContent>
        </Card>

        <Card data-testid="avg-latency-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Latency</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.avg_latency || 0}ms</div>
            <p className="text-xs text-muted-foreground">this week</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card data-testid="weekly-summary-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-primary" />
              Weekly Summary
            </CardTitle>
            <CardDescription>Performance overview for the last 7 days</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Total Checks</span>
              <span className="font-semibold">{stats?.total_checks || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Uptime</span>
              <span className="font-semibold text-green-500">{stats?.uptime_percentage || 0}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Average Latency</span>
              <span className="font-semibold">{stats?.avg_latency || 0}ms</span>
            </div>
            {stats?.improvement && (
              <div className="mt-4 p-3 bg-primary/10 rounded-lg border border-primary/20">
                <p className="text-sm font-medium text-primary mb-1">Improvement Tip</p>
                <p className="text-sm text-muted-foreground">{stats.improvement}</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card data-testid="recent-websites-card">
          <CardHeader>
            <CardTitle>Recent Websites</CardTitle>
            <CardDescription>Your most recently added websites</CardDescription>
          </CardHeader>
          <CardContent>
            {websites.length === 0 ? (
              <p className="text-center text-muted-foreground py-8">No websites added yet</p>
            ) : (
              <div className="space-y-3">
                {websites.slice(0, 5).map((website) => (
                  <div
                    key={website.id}
                    className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-accent/50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-2 h-2 rounded-full ${
                          website.status === 'online'
                            ? 'status-online'
                            : website.status === 'offline'
                            ? 'status-offline'
                            : 'status-unknown'
                        }`}
                      ></div>
                      <div>
                        <p className="font-medium text-sm">{website.name}</p>
                        <p className="text-xs text-muted-foreground">{website.url}</p>
                      </div>
                    </div>
                    <span
                      className={`text-xs px-2 py-1 rounded-full ${
                        website.status === 'online'
                          ? 'bg-green-500/10 text-green-500'
                          : website.status === 'offline'
                          ? 'bg-red-500/10 text-red-500'
                          : 'bg-gray-500/10 text-gray-500'
                      }`}
                    >
                      {website.status}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default OverviewPage;
