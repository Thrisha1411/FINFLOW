import React, { useEffect, useState } from 'react';
import { Repeat, Calendar, DollarSign, AlertCircle, Plus } from 'lucide-react';
import api from '../api/client';
import type { Subscription } from '../types';

export const SubscriptionsPage: React.FC = () => {
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [detected, setDetected] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSubData = async () => {
      try {
        const [sRes, aRes, dRes] = await Promise.all([
          api.get('/subscriptions'),
          api.get('/subscriptions/analytics'),
          api.get('/subscriptions/detected')
        ]);
        setSubscriptions(sRes.data);
        setAnalytics(aRes.data);
        setDetected(dRes.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchSubData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Recurring Subscription Management</h1>
        <p className="text-sm text-slate-400 mt-1">
          Automated recurring cadence detection, renewal alerts, and cost projections.
        </p>
      </div>

      {/* Analytics KPI row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase">Active Subscriptions</span>
          <div className="mt-2 text-2xl font-bold text-white">{analytics?.active_subscriptions_count || 0}</div>
          <p className="text-xs text-slate-400 mt-1">Monitored corporate services</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase">Monthly Recurring Spend</span>
          <div className="mt-2 text-2xl font-bold text-indigo-400">
            ${analytics?.monthly_recurring_spend?.toLocaleString('en-US', { minimumFractionDigits: 2 }) || '0.00'}
          </div>
          <p className="text-xs text-slate-400 mt-1">Fixed monthly overhead</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase">Annual Projected Cost</span>
          <div className="mt-2 text-2xl font-bold text-white">
            ${analytics?.annual_projected_spend?.toLocaleString('en-US', { minimumFractionDigits: 2 }) || '0.00'}
          </div>
          <p className="text-xs text-slate-400 mt-1">12-month run-rate projection</p>
        </div>
      </div>

      {/* Subscriptions Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <h2 className="text-base font-semibold text-white">Active Subscriptions</h2>
          <span className="text-xs text-slate-400">Tracked SaaS & Services</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/40 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                <th className="py-3 px-6">Service / Merchant</th>
                <th className="py-3 px-6">Amount</th>
                <th className="py-3 px-6">Billing Cadence</th>
                <th className="py-3 px-6">Next Renewal</th>
                <th className="py-3 px-6">Status</th>
                <th className="py-3 px-6">Detection Source</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-sm">
              {subscriptions.map((s) => (
                <tr key={s.id} className="hover:bg-slate-800/40 transition">
                  <td className="py-3.5 px-6 font-semibold text-white">{s.merchant_name}</td>
                  <td className="py-3.5 px-6 font-bold text-slate-200">${s.amount.toFixed(2)}</td>
                  <td className="py-3.5 px-6 font-mono text-xs text-slate-400">{s.billing_cycle}</td>
                  <td className="py-3.5 px-6 text-xs text-slate-300">
                    {new Date(s.next_renewal_date).toLocaleDateString()}
                  </td>
                  <td className="py-3.5 px-6">
                    <span className="px-2 py-0.5 rounded text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                      {s.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-6">
                    <span className="text-xs text-slate-400 font-mono">
                      {s.is_auto_detected ? 'AUTO_CADENCE_ML' : 'MANUAL_ENTRY'}
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
