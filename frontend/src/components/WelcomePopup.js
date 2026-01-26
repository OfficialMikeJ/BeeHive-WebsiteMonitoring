import React, { useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { X, TrendingUp, Activity, Clock } from 'lucide-react';

const WelcomePopup = ({ stats, onClose, username }) => {
  useEffect(() => {
    // Auto-close after 10 seconds
    const timer = setTimeout(() => {
      onClose();
    }, 10000);

    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in" data-testid="welcome-popup">
      <Card className="max-w-md w-full border-2 border-primary">
        <CardHeader className="relative">
          <Button
            data-testid="close-welcome-popup-button"
            variant="ghost"
            size="icon"
            className="absolute right-2 top-2"
            onClick={onClose}
          >
            <X className="h-4 w-4" />
          </Button>
          <CardTitle className="text-2xl" style={{ fontFamily: 'Work Sans, sans-serif' }}>
            Welcome Back, {username}! 👋
          </CardTitle>
          <CardDescription>Here's your weekly roundup</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm">{stats.message}</p>

          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-accent/50 rounded-lg">
              <div className="flex items-center gap-2">
                <Activity className="h-4 w-4 text-primary" />
                <span className="text-sm font-medium">Total Checks</span>
              </div>
              <span className="font-bold">{stats.total_checks}</span>
            </div>

            <div className="flex items-center justify-between p-3 bg-accent/50 rounded-lg">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-green-500" />
                <span className="text-sm font-medium">Uptime</span>
              </div>
              <span className="font-bold text-green-500">{stats.uptime_percentage}%</span>
            </div>

            <div className="flex items-center justify-between p-3 bg-accent/50 rounded-lg">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-primary" />
                <span className="text-sm font-medium">Avg Latency</span>
              </div>
              <span className="font-bold">{stats.avg_latency}ms</span>
            </div>
          </div>

          {stats.improvement && (
            <div className="mt-4 p-3 bg-primary/10 rounded-lg border border-primary/20">
              <p className="text-sm font-medium text-primary mb-1">💡 Improvement Suggestion</p>
              <p className="text-sm text-muted-foreground">{stats.improvement}</p>
            </div>
          )}

          <Button data-testid="got-it-button" onClick={onClose} className="w-full mt-4">
            Got it!
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default WelcomePopup;
