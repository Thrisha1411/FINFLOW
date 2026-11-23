import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  ArrowLeftRight,
  ShieldAlert,
  Receipt,
  Bot,
  TrendingUp,
  PieChart,
  Repeat,
  Sliders,
  SearchCode,
  FileText,
  Bell,
  Settings,
  ShieldCheck,
  Building2
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const Sidebar: React.FC = () => {
  const { user } = useAuth();

  const navItems = [
    { name: 'Overview', path: '/', icon: LayoutDashboard },
    { name: 'Transactions', path: '/transactions', icon: ArrowLeftRight },
    { name: 'Fraud Intelligence', path: '/fraud', icon: ShieldAlert },
    { name: 'Receipt Scanner', path: '/receipts', icon: Receipt },
    { name: 'AI Assistant', path: '/assistant', icon: Bot },
    { name: 'Analytics & Forecast', path: '/analytics', icon: TrendingUp },
    { name: 'Budget Planner (50/30/20)', path: '/budgets', icon: PieChart },
    { name: 'Subscriptions', path: '/subscriptions', icon: Repeat },
    { name: 'What-If Simulator', path: '/simulator', icon: Sliders },
    { name: 'Root Cause Analysis', path: '/root-cause', icon: SearchCode },
    { name: 'Audit Logs', path: '/audit', icon: FileText },
    { name: 'Notifications', path: '/notifications', icon: Bell },
    { name: 'Settings & 2FA', path: '/settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col h-screen select-none sticky top-0">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800 gap-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <ShieldCheck className="w-5 h-5 text-white" />
        </div>
        <div>
          <span className="font-bold text-lg text-white tracking-tight">FinFlow</span>
          <span className="text-xs ml-1 font-semibold px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">AI</span>
        </div>
      </div>

      {/* Organization Badge */}
      <div className="px-4 py-3 border-b border-slate-800/60 bg-slate-950/40">
        <div className="flex items-center gap-2.5 px-3 py-2 rounded-lg bg-slate-800/50 border border-slate-700/50">
          <Building2 className="w-4 h-4 text-cyan-400 shrink-0" />
          <div className="overflow-hidden">
            <p className="text-xs font-medium text-slate-200 truncate">Acme Financial Corp</p>
            <p className="text-[10px] text-slate-400 font-mono">ORG_ADMIN • USD</p>
          </div>
        </div>
      </div>

      {/* Nav Menu */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span className="truncate">{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* User profile footer */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/40 flex items-center justify-center font-bold text-xs">
            {user?.full_name ? user.full_name[0] : 'U'}
          </div>
          <div className="overflow-hidden">
            <p className="text-xs font-semibold text-white truncate">{user?.full_name || 'Finance User'}</p>
            <p className="text-[10px] text-slate-400 truncate">{user?.email || 'user@finflow.ai'}</p>
          </div>
        </div>
      </div>
    </aside>
  );
};
