import React, { useEffect, useState } from 'react';
import { PieChart, CheckCircle, AlertTriangle, ShieldCheck, ArrowRight, Lightbulb, Sparkles } from 'lucide-react';
import api from '../api/client';
import type { Budget503020, HealthScore } from '../types';

export const BudgetPage: React.FC = () => {
  const [budget, setBudget] = useState<Budget503020 | null>(null);
  const [health, setHealth] = useState<HealthScore | null>(null);
  const [nextPlan, setNextPlan] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBudgetData = async () => {
      try {
        const [bRes, hRes, pRes] = await Promise.all([
          api.get('/budgets/50-30-20'),
          api.get('/budgets/health-score'),
          api.get('/budgets/next-month-plan')
        ]);
        setBudget(bRes.data);
        setHealth(hRes.data);
        setNextPlan(pRes.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchBudgetData();
  }, []);

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
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Smart Budgeting & 50/30/20 Framework</h1>
        <p className="text-sm text-slate-400 mt-1">
          Algorithmic classification into Needs, Wants, and Savings, paired with evidence-based next-month planning.
        </p>
      </div>

      {/* 50/30/20 Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Needs (Target 50%) */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">Essential Needs</span>
            <span className="text-xs font-bold text-slate-400">Target: 50%</span>
          </div>
          <div>
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-bold text-white">{budget?.needs.actual_percentage}%</span>
              <span className="text-sm font-semibold text-slate-300">
                ${budget?.needs.amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </span>
            </div>
            <div className="w-full bg-slate-800 h-2.5 rounded-full mt-2 overflow-hidden">
              <div
                className="bg-indigo-500 h-full rounded-full"
                style={{ width: `${Math.min(100, budget?.needs.actual_percentage || 0)}%` }}
              ></div>
            </div>
          </div>
          <div className="text-xs text-slate-400">
            Rent, utilities, cloud infrastructure, healthcare, insurance, and payroll taxes.
          </div>
        </div>

        {/* Wants (Target 30%) */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-rose-400 uppercase tracking-wider">Discretionary Wants</span>
            <span className="text-xs font-bold text-slate-400">Target: 30%</span>
          </div>
          <div>
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-bold text-white">{budget?.wants.actual_percentage}%</span>
              <span className="text-sm font-semibold text-slate-300">
                ${budget?.wants.amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </span>
            </div>
            <div className="w-full bg-slate-800 h-2.5 rounded-full mt-2 overflow-hidden">
              <div
                className="bg-rose-500 h-full rounded-full"
                style={{ width: `${Math.min(100, budget?.wants.actual_percentage || 0)}%` }}
              ></div>
            </div>
          </div>
          <div className="text-xs text-slate-400">
            Shopping, team dining, entertainment, travel, and non-essential incidental software.
          </div>
        </div>

        {/* Savings & Investments (Target 20%) */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Savings & Reserves</span>
            <span className="text-xs font-bold text-slate-400">Target: 20%</span>
          </div>
          <div>
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-bold text-white">{budget?.savings.actual_percentage}%</span>
              <span className="text-sm font-semibold text-slate-300">
                ${budget?.savings.amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </span>
            </div>
            <div className="w-full bg-slate-800 h-2.5 rounded-full mt-2 overflow-hidden">
              <div
                className="bg-emerald-500 h-full rounded-full"
                style={{ width: `${Math.min(100, budget?.savings.actual_percentage || 0)}%` }}
              ></div>
            </div>
          </div>
          <div className="text-xs text-slate-400">
            Emergency liquidity reserve, treasury investments, and debt paydown funds.
          </div>
        </div>
      </div>

      {/* Health Score Pillar Breakdown */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800 pb-4 mb-4 gap-2">
          <div>
            <h2 className="text-base font-bold text-white">Transparent Budget Health Score</h2>
            <p className="text-xs text-slate-400">Deterministic calculation across 5 weighted pillars</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-2xl font-bold text-white">{health?.health_score}/100</span>
            <span className="text-xs font-semibold px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              {health?.rating}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {health?.pillars &&
            Object.entries(health.pillars).map(([k, p]: any) => (
              <div key={k} className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="font-medium text-slate-300 capitalize">{k.replace('_', ' ')}</span>
                  <span className="font-bold text-indigo-400">
                    {p.score}/{p.max}
                  </span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-indigo-500 h-full rounded-full"
                    style={{ width: `${(p.score / p.max) * 100}%` }}
                  ></div>
                </div>
                <p className="text-[11px] text-slate-400">{p.details}</p>
              </div>
            ))}
        </div>
      </div>

      {/* Next-Month Budget Planner */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Sparkles className="w-5 h-5 text-indigo-400" />
            <div>
              <h2 className="text-base font-bold text-white">
                Next-Month Budget Planner ({nextPlan?.target_month})
              </h2>
              <p className="text-xs text-slate-400">Evidence-backed limits proposed from verified spending</p>
            </div>
          </div>
          <span className="text-xs px-2.5 py-1 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-semibold">
            Status: {nextPlan?.status}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/40 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                <th className="py-2.5 px-4">Category</th>
                <th className="py-2.5 px-4">Group</th>
                <th className="py-2.5 px-4">Recommended Limit</th>
                <th className="py-2.5 px-4">Reasoning / Data Evidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-xs">
              {nextPlan?.category_limits.map((cl: any, idx: number) => (
                <tr key={idx} className="hover:bg-slate-800/40">
                  <td className="py-3 px-4 font-semibold text-white">{cl.category}</td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded bg-slate-800 font-mono text-[10px] text-slate-300">
                      {cl.group}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-bold text-indigo-400">${cl.recommended_limit.toLocaleString()}</td>
                  <td className="py-3 px-4 text-slate-300">{cl.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
