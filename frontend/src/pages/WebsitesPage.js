import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { toast } from 'sonner';
import { Plus, Trash2, RefreshCw, Activity, TrendingUp } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const WebsitesPage = ({ user }) => {
  const [websites, setWebsites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [newWebsite, setNewWebsite] = useState({ name: '', url: '' });
  const [selectedWebsite, setSelectedWebsite] = useState(null);
  const [monitoringData, setMonitoringData] = useState([]);
  const [checking, setChecking] = useState({});

  useEffect(() => {
    fetchWebsites();
  }, []);

  const fetchWebsites = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/websites`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setWebsites(response.data);
    } catch (error) {
      toast.error('Failed to fetch websites');
    } finally {
      setLoading(false);
    }
  };

  const handleAddWebsite = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/websites`, newWebsite, {
        headers: { Authorization: `Bearer ${token}` },
      });
      toast.success('Website added successfully');
      setAddDialogOpen(false);
      setNewWebsite({ name: '', url: '' });
      fetchWebsites();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add website');
    }
  };

  const handleDeleteWebsite = async (id) => {
    if (!window.confirm('Are you sure you want to delete this website?')) return;

    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API}/websites/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      toast.success('Website deleted successfully');
      fetchWebsites();
    } catch (error) {
      toast.error('Failed to delete website');
    }
  };

  const handleCheckWebsite = async (id) => {
    setChecking({ ...checking, [id]: true });
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/websites/${id}/check`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      toast.success('Website check initiated');
      setTimeout(() => {
        fetchWebsites();
        setChecking({ ...checking, [id]: false });
      }, 2000);
    } catch (error) {
      toast.error('Failed to check website');
      setChecking({ ...checking, [id]: false });
    }
  };

  const fetchMonitoringData = async (websiteId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/monitoring/${websiteId}?limit=20`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMonitoringData(response.data.reverse());
    } catch (error) {
      console.error('Error fetching monitoring data:', error);
    }
  };

  const handleViewDetails = (website) => {
    setSelectedWebsite(website);
    fetchMonitoringData(website.id);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="websites-page">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold mb-2" style={{ fontFamily: 'Work Sans, sans-serif' }}>
            Websites
          </h2>
          <p className="text-muted-foreground">Manage and monitor your websites</p>
        </div>
        <Dialog open={addDialogOpen} onOpenChange={setAddDialogOpen}>
          <DialogTrigger asChild>
            <Button data-testid="add-website-button">
              <Plus className="h-4 w-4 mr-2" />
              Add Website
            </Button>
          </DialogTrigger>
          <DialogContent data-testid="add-website-dialog">
            <DialogHeader>
              <DialogTitle>Add New Website</DialogTitle>
              <DialogDescription>
                Add a website to start monitoring its performance
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleAddWebsite} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Website Name</Label>
                <Input
                  data-testid="website-name-input"
                  id="name"
                  placeholder="My Website"
                  value={newWebsite.name}
                  onChange={(e) => setNewWebsite({ ...newWebsite, name: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="url">Website URL</Label>
                <Input
                  data-testid="website-url-input"
                  id="url"
                  type="url"
                  placeholder="https://example.com"
                  value={newWebsite.url}
                  onChange={(e) => setNewWebsite({ ...newWebsite, url: e.target.value })}
                  required
                />
              </div>
              <Button data-testid="submit-website-button" type="submit" className="w-full">
                Add Website
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {websites.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Activity className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground text-center">No websites added yet</p>
            <Button className="mt-4" onClick={() => setAddDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Your First Website
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {websites.map((website) => (
            <Card key={website.id} className="website-card" data-testid={`website-card-${website.id}`}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="flex items-center gap-2">
                      <div
                        className={`w-3 h-3 rounded-full ${
                          website.status === 'online'
                            ? 'status-online'
                            : website.status === 'offline'
                            ? 'status-offline'
                            : 'status-unknown'
                        }`}
                      ></div>
                      {website.name}
                    </CardTitle>
                    <CardDescription className="mt-1">{website.url}</CardDescription>
                  </div>
                  <span
                    className={`text-xs px-2 py-1 rounded-full capitalize ${
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
              </CardHeader>
              <CardContent>
                <div className="flex gap-2">
                  <Button
                    data-testid={`check-website-${website.id}-button`}
                    size="sm"
                    onClick={() => handleCheckWebsite(website.id)}
                    disabled={checking[website.id]}
                  >
                    <RefreshCw className={`h-4 w-4 mr-2 ${checking[website.id] ? 'animate-spin' : ''}`} />
                    Check Now
                  </Button>
                  <Button
                    data-testid={`view-details-${website.id}-button`}
                    size="sm"
                    variant="outline"
                    onClick={() => handleViewDetails(website)}
                  >
                    <TrendingUp className="h-4 w-4 mr-2" />
                    View Details
                  </Button>
                  <Button
                    data-testid={`delete-website-${website.id}-button`}
                    size="sm"
                    variant="destructive"
                    onClick={() => handleDeleteWebsite(website.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Monitoring Details Dialog */}
      <Dialog open={!!selectedWebsite} onOpenChange={() => setSelectedWebsite(null)}>
        <DialogContent className="max-w-3xl" data-testid="monitoring-details-dialog">
          <DialogHeader>
            <DialogTitle>{selectedWebsite?.name}</DialogTitle>
            <DialogDescription>{selectedWebsite?.url}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {monitoringData.length > 0 ? (
              <>
                <div>
                  <h4 className="text-sm font-medium mb-2">Latency Over Time</h4>
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={monitoringData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="timestamp"
                        tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                      />
                      <YAxis />
                      <Tooltip
                        labelFormatter={(value) => new Date(value).toLocaleString()}
                      />
                      <Line type="monotone" dataKey="latency" stroke="hsl(var(--primary))" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-3 bg-accent/50 rounded-lg">
                    <p className="text-xs text-muted-foreground">Avg Latency</p>
                    <p className="text-lg font-bold">
                      {(
                        monitoringData.reduce((acc, curr) => acc + (curr.latency || 0), 0) /
                        monitoringData.length
                      ).toFixed(2)}
                      ms
                    </p>
                  </div>
                  <div className="p-3 bg-accent/50 rounded-lg">
                    <p className="text-xs text-muted-foreground">Total Checks</p>
                    <p className="text-lg font-bold">{monitoringData.length}</p>
                  </div>
                  <div className="p-3 bg-accent/50 rounded-lg">
                    <p className="text-xs text-muted-foreground">Uptime</p>
                    <p className="text-lg font-bold text-green-500">
                      {(
                        (monitoringData.filter((d) => d.is_online).length / monitoringData.length) *
                        100
                      ).toFixed(1)}
                      %
                    </p>
                  </div>
                </div>
              </>
            ) : (
              <p className="text-center text-muted-foreground py-8">No monitoring data available</p>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default WebsitesPage;
