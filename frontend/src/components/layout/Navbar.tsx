import React from 'react';
import { Bell, LogOut, ShieldCheck, Activity } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="h-16 bg-slate-900/80 backdrop-blur border-b border-slate-800 px-8 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="text-xs font-semibold text-emerald-400">Live Orchestration Stream</span>
        </div>
        <span className="text-xs text-slate-500 font-mono hidden md:inline">FinFlow Core v1.0.0</span>
      </div>

      <div className="flex items-center gap-4">
        {/* Quick notification indicator */}
        <button
          onClick={() => navigate('/notifications')}
          className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition relative"
          title="Notifications"
        >
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-rose-500 ring-2 ring-slate-900"></span>
        </button>

        {/* User Info & Logout */}
        <div className="flex items-center gap-3 pl-4 border-l border-slate-800">
          <div className="text-right hidden sm:block">
            <div className="text-xs font-medium text-slate-200">{user?.full_name}</div>
            <div className="text-[10px] text-indigo-400 font-semibold">{user?.role}</div>
          </div>
          <button
            onClick={handleLogout}
            className="p-2 text-slate-400 hover:text-rose-400 rounded-lg hover:bg-slate-800 transition"
            title="Log out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
