import React, { useEffect, useState } from 'react';
import {
  DollarSign,
  TrendingUp,
  ShieldAlert,
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  PieChart as PieIcon,
  CreditCard,
  RefreshCw
} from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, PieChart, Pie, Cell } from 'recharts';
import api from '../api/client';
import type { DashboardMetrics, Transaction } from '../types';

export const OverviewPage: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [recentTxs, setRecentTxs] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchOverview = async () => {
    try {
      const res = await api.get('/dashboard/overview');
      setMetrics(res.data.metrics);
      setRecentTxs(res.data.recent_transactions);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverview();
  }, []);

  const monthlyTrendData = [
    { month: 'Jul', expenses: 14200, income: 28000 },
    { month: 'Aug', expenses: 16800, income: 29500 },
    { month: 'Sep', expenses: 15400, income: 30000 },
    { month: 'Oct', expenses: 17200, income: 31000 },
    { month: 'Nov', expenses: metrics ? metrics.total_expenses : 14800, income: metrics ? metrics.total_income : 30500 },
  ];

  const categoryBreakdown = [
    { name: 'Rent & Facilities', value: 3500, color: '#6366f1' },
    { name: 'Business Cloud/SaaS', value: 4800, color: '#06b6d4' },
    { name: 'Healthcare/Insurance', value: 3250, color: '#f59e0b' },
    { name: 'Shopping & Fleet', value: 2400, color: '#ec4899' },
    { name: 'Dining & Other', value: 850, color: '#10b981' },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Financial Operations Hub</h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time multi-tenant telemetry, automated fraud defense, and cash flow intelligence.
          </p>
        </div>
        <button
          onClick={fetchOverview}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-sm font-medium border border-slate-700 transition"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh Metrics
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Total Income */}
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium uppercase tracking-wider">
            <span>Total Monthly Inflow</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <ArrowDownRight className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-2xl font-bold text-white">
              ${metrics?.total_income.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </span>
          </div>
          <p className="text-xs text-emerald-400 mt-2 flex items-center gap-1 font-medium">
            <TrendingUp className="w-3.5 h-3.5" /> +4.2% vs previous month
          </p>
        </div>

        {/* Total Expenses */}
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium uppercase tracking-wider">
            <span>Total Monthly Outflow</span>
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
              <ArrowUpRight className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-2xl font-bold text-white">
              ${metrics?.total_expenses.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Settled across {metrics?.total_transactions_count} corporate card / wire events
          </p>
        </div>

        {/* Net Cash Flow & Savings Rate */}
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium uppercase tracking-wider">
            <span>Net Cash Flow</span>
            <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-2xl font-bold text-cyan-400">
              +${metrics?.net_cashflow.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </span>
          </div>
          <p className="text-xs text-slate-300 mt-2">
            Savings Rate: <strong className="text-white">{metrics?.savings_rate_percentage}%</strong> (Target: 20%)
          </p>
        </div>

        {/* Health Score & Fraud Alerts */}
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium uppercase tracking-wider">
            <span>Budget Health Score</span>
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
              <ShieldAlert className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white">{metrics?.financial_health_score}/100</span>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              {metrics?.financial_health_rating}
            </span>
          </div>
          <p className="text-xs text-rose-400 mt-2 font-medium">
            {metrics?.active_fraud_alerts} active high-risk fraud cases under review
          </p>
        </div>
      </div>

      {/* Analytics & Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Area Chart */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-semibold text-white">Cash Flow & Expense Velocity</h2>
              <p className="text-xs text-slate-400">Historical verified cash flow performance</p>
            </div>
            <span className="text-xs font-mono text-slate-400">5-Month Inflow vs Outflow</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={monthlyTrendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="incomeGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="expenseGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="month" stroke="#64748b" fontSize={12} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={12} tickLine={false} tickFormatter={(v) => `$${v / 1000}k`} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px' }}
                  formatter={(val: any) => [`$${Number(val || 0).toLocaleString()}`, '']}
                />
                <Area type="monotone" dataKey="income" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#incomeGradient)" name="Income" />
                <Area type="monotone" dataKey="expenses" stroke="#6366f1" strokeWidth={2} fillOpacity={1} fill="url(#expenseGradient)" name="Expenses" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Donut Breakdown */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl flex flex-col justify-between">
          <div>
            <h2 className="text-base font-semibold text-white">Expense Distribution</h2>
            <p className="text-xs text-slate-400 mb-4">By category allocations</p>
            <div className="h-44">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryBreakdown}
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={65}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {categoryBreakdown.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px' }}
                    formatter={(val: any) => [`$${Number(val || 0).toLocaleString()}`, '']}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="space-y-2 mt-2">
            {categoryBreakdown.slice(0, 4).map((c) => (
              <div key={c.name} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: c.color }}></span>
                  <span className="text-slate-300">{c.name}</span>
                </div>
                <span className="font-semibold text-white">${c.value.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Transactions Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <CreditCard className="w-4 h-4 text-indigo-400" />
            <h2 className="text-base font-semibold text-white">Recent Financial Operations</h2>
          </div>
          <span className="text-xs text-slate-400">Live transaction stream</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800/80 bg-slate-950/30 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                <th className="py-3 px-6">Reference ID</th>
                <th className="py-3 px-6">Merchant / Payee</th>
                <th className="py-3 px-6">Amount</th>
                <th className="py-3 px-6">Status</th>
                <th className="py-3 px-6">Risk Score</th>
                <th className="py-3 px-6">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-sm">
              {recentTxs.map((tx) => {
                const isIncome = tx.amount < 0;
                return (
                  <tr key={tx.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-6 font-mono text-xs text-slate-300">{tx.reference_id}</td>
                    <td className="py-3.5 px-6 font-medium text-white">{tx.merchant_name}</td>
                    <td className={`py-3.5 px-6 font-semibold ${isIncome ? 'text-emerald-400' : 'text-slate-100'}`}>
                      {isIncome ? `+$${Math.abs(tx.amount).toFixed(2)}` : `$${tx.amount.toFixed(2)}`}
                    </td>
                    <td className="py-3.5 px-6">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                          tx.status === 'SUCCESS'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                            : tx.status === 'FLAGGED'
                            ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                            : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                        }`}
                      >
                        {tx.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-6">
                      <span
                        className={`text-xs font-semibold ${
                          tx.risk_score > 60 ? 'text-rose-400' : tx.risk_score > 30 ? 'text-amber-400' : 'text-emerald-400'
                        }`}
                      >
                        {tx.risk_score}/100 ({tx.risk_level})
                      </span>
                    </td>
                    <td className="py-3.5 px-6 text-xs text-slate-400">
                      {new Date(tx.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
