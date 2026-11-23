import React from 'react';
import { TrendingUp, AlertTriangle, ShieldCheck, ArrowRight, Calendar } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, BarChart, Bar } from 'recharts';

export const AnalyticsPage: React.FC = () => {
  const forecastTrend = [
    { month: 'Jul', actual: 14200, forecast: null, lower: null, upper: null },
    { month: 'Aug', actual: 16800, forecast: null, lower: null, upper: null },
    { month: 'Sep', actual: 15400, forecast: null, lower: null, upper: null },
    { month: 'Oct', actual: 17200, forecast: null, lower: null, upper: null },
    { month: 'Nov (Current)', actual: 14800, forecast: 14800, lower: 14800, upper: 14800 },
    { month: 'Dec (Forecast)', actual: null, forecast: 15600, lower: 14100, upper: 17100 },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Predictive Spending & Cash Flow Forecast</h1>
        <p className="text-sm text-slate-400 mt-1">
          Holt Linear Exponential Smoothing model projecting future month commitments with 95% confidence intervals.
        </p>
      </div>

      {/* Forecast Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase">Projected Next Month</span>
          <div className="mt-2 text-2xl font-bold text-white">$15,600.00</div>
          <p className="text-xs text-indigo-400 mt-1 font-medium">Holt's Linear Smoothing</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase">95% Confidence Bounds</span>
          <div className="mt-2 text-xl font-bold text-cyan-400">$14,100 — $17,100</div>
          <p className="text-xs text-slate-400 mt-1">Standard error margin: $1,500</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase">Overspending Probability</span>
          <div className="mt-2 text-2xl font-bold text-emerald-400">28.0%</div>
          <p className="text-xs text-emerald-400 mt-1">Low probability of exceeding budget</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase">Fixed SaaS Commitments</span>
          <div className="mt-2 text-2xl font-bold text-white">$4,365.50</div>
          <p className="text-xs text-slate-400 mt-1">Active recurring verified subscriptions</p>
        </div>
      </div>

      {/* Projection Chart */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-semibold text-white">Historical vs Predictive Expenditure Curve</h2>
            <p className="text-xs text-slate-400">Historical verified spend vs projected 1-step Holt forecast</p>
          </div>
          <span className="text-xs px-2.5 py-1 rounded bg-slate-800 font-mono text-indigo-400 border border-slate-700">
            Model: EXPONENTIAL_SMOOTHING_HOLT
          </span>
        </div>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={forecastTrend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="actualGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="forecastGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="month" stroke="#64748b" fontSize={12} tickLine={false} />
              <YAxis stroke="#64748b" fontSize={12} tickLine={false} tickFormatter={(v) => `$${v / 1000}k`} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px' }}
                formatter={(val: any) => [`$${Number(val || 0).toLocaleString()}`, '']}
              />
              <Area type="monotone" dataKey="actual" stroke="#6366f1" strokeWidth={2} fillOpacity={1} fill="url(#actualGrad)" name="Actual Verified Spend" />
              <Area type="monotone" dataKey="forecast" stroke="#06b6d4" strokeWidth={2} strokeDasharray="5 5" fillOpacity={1} fill="url(#forecastGrad)" name="Next Month Projected" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
