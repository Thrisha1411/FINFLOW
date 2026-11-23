import React, { useEffect, useState } from 'react';
import { SearchCode, TrendingUp, TrendingDown, ArrowRight } from 'lucide-react';
import api from '../api/client';

export const RootCausePage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRootCause = async () => {
      try {
        const res = await api.get('/root-cause/analyze');
        setData(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchRootCause();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">AI Financial Root Cause Analysis</h1>
        <p className="text-sm text-slate-400 mt-1">
          Deconstructs period-over-period budget variances and isolates the underlying category and merchant drivers.
        </p>
      </div>

      {/* Summary Card */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800 pb-3 gap-2">
          <span className="text-sm font-semibold text-slate-300">
            Comparison Periods: {data?.current_period} vs {data?.comparison_period}
          </span>
          <span className="text-xs px-2.5 py-1 rounded bg-slate-800 text-indigo-400 font-mono">
            Variance: {data?.summary.expense_percentage_change}%
          </span>
        </div>

        <div className="text-sm text-slate-200 leading-relaxed font-medium">
          {data?.actionable_findings?.[0]}
        </div>
      </div>

      {/* Primary Drivers Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800">
          <h2 className="text-base font-semibold text-white">Primary Variance Contributors</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/40 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                <th className="py-3 px-6">Category</th>
                <th className="py-3 px-6">Current Period</th>
                <th className="py-3 px-6">Prior Period</th>
                <th className="py-3 px-6">Dollar Variance</th>
                <th className="py-3 px-6">Percentage Change</th>
                <th className="py-3 px-6">Impact Type</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-xs">
              {data?.primary_drivers?.map((d: any, idx: number) => (
                <tr key={idx} className="hover:bg-slate-800/40">
                  <td className="py-3.5 px-6 font-semibold text-white">{d.category}</td>
                  <td className="py-3.5 px-6 font-mono">${d.current_amount.toFixed(2)}</td>
                  <td className="py-3.5 px-6 font-mono text-slate-400">${d.previous_amount.toFixed(2)}</td>
                  <td
                    className={`py-3.5 px-6 font-mono font-bold ${
                      d.dollar_difference > 0 ? 'text-rose-400' : 'text-emerald-400'
                    }`}
                  >
                    {d.dollar_difference > 0 ? `+$${d.dollar_difference.toFixed(2)}` : `-$${Math.abs(d.dollar_difference).toFixed(2)}`}
                  </td>
                  <td className="py-3.5 px-6 font-semibold">{d.percentage_change}%</td>
                  <td className="py-3.5 px-6">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        d.impact === 'INCREASED_EXPENSE'
                          ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                          : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                      }`}
                    >
                      {d.impact}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
