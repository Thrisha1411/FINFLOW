import React, { useEffect, useState } from 'react';
import { Bell, CheckCheck, AlertTriangle, ShieldAlert, Sparkles } from 'lucide-react';
import api from '../api/client';
import type { Notification } from '../types';

export const NotificationsPage: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchNotifs = async () => {
    try {
      const res = await api.get('/notifications');
      setNotifications(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifs();
  }, []);

  const handleMarkRead = async (id: string) => {
    try {
      await api.patch(`/notifications/${id}/read`);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Notifications & Real-Time Signals</h1>
        <p className="text-sm text-slate-400 mt-1">
          System events, automated fraud alerts, and 50/30/20 threshold warnings.
        </p>
      </div>

      <div className="space-y-3">
        {notifications.map((n) => (
          <div
            key={n.id}
            className={`p-4 rounded-xl border transition flex items-start justify-between ${
              n.is_read
                ? 'bg-slate-900/60 border-slate-800'
                : 'bg-slate-900 border-indigo-500/40 shadow-sm shadow-indigo-500/5'
            }`}
          >
            <div className="flex items-start gap-3.5">
              <div
                className={`p-2.5 rounded-lg shrink-0 ${
                  n.type === 'FRAUD_ALERT'
                    ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                    : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                }`}
              >
                {n.type === 'FRAUD_ALERT' ? (
                  <ShieldAlert className="w-5 h-5" />
                ) : (
                  <AlertTriangle className="w-5 h-5" />
                )}
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-semibold text-white">{n.title}</h3>
                  {!n.is_read && (
                    <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
                  )}
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">{n.message}</p>
                <span className="text-[10px] text-slate-500 font-mono">
                  {new Date(n.created_at).toLocaleString()}
                </span>
              </div>
            </div>

            {!n.is_read && (
              <button
                onClick={() => handleMarkRead(n.id)}
                className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium transition"
              >
                <CheckCheck className="w-3.5 h-3.5" />
                Mark as read
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
