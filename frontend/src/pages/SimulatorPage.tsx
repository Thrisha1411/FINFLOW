import React, { useState } from 'react';
import { Sliders, TrendingUp, Sparkles, AlertCircle } from 'lucide-react';
import api from '../api/client';

export const SimulatorPage: React.FC = () => {
  const [shoppingReduction, setShoppingReduction] = useState(15);
  const [diningReduction, setDiningReduction] = useState(20);
  const [incomeDelta, setIncomeDelta] = useState(1000);
  const [additionalSavings, setAdditionalSavings] = useState(500);

  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const runSimulation = async () => {
    setLoading(true);
    try {
      const res = await api.post('/simulator/simulate', {
        shopping_reduction_pct: shoppingReduction,
        dining_reduction_pct: diningReduction,
        income_delta: incomeDelta,
        additional_monthly_savings: additionalSavings,
      });
      setResult(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    runSimulation();
  }, [shoppingReduction, diningReduction, incomeDelta, additionalSavings]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">AI What-If Financial Scenario Simulator</h1>
        <p className="text-sm text-slate-400 mt-1">
          Simulate budget contractions, revenue expansions, or subscription cancellations on cash-flow and goal timelines.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls Column */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
          <h2 className="text-base font-semibold text-white">Hypothetical Levers</h2>

          <div>
            <div className="flex justify-between text-xs mb-1.5">
              <span className="text-slate-300">Reduce Shopping Spend</span>
              <span className="font-bold text-indigo-400">{shoppingReduction}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="50"
              value={shoppingReduction}
              onChange={(e) => setShoppingReduction(Number(e.target.value))}
              className="w-full accent-indigo-500"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs mb-1.5">
              <span className="text-slate-300">Reduce Dining / Discretionary</span>
              <span className="font-bold text-indigo-400">{diningReduction}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="50"
              value={diningReduction}
              onChange={(e) => setDiningReduction(Number(e.target.value))}
              className="w-full accent-indigo-500"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs mb-1.5">
              <span className="text-slate-300">Monthly Revenue Expansion</span>
              <span className="font-bold text-emerald-400">+${incomeDelta}</span>
            </div>
            <input
              type="range"
              min="0"
              max="10000"
              step="500"
              value={incomeDelta}
              onChange={(e) => setIncomeDelta(Number(e.target.value))}
              className="w-full accent-emerald-500"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs mb-1.5">
              <span className="text-slate-300">Direct Additional Reserve Deposit</span>
              <span className="font-bold text-cyan-400">+${additionalSavings}/mo</span>
            </div>
            <input
              type="range"
              min="0"
              max="5000"
              step="100"
              value={additionalSavings}
              onChange={(e) => setAdditionalSavings(Number(e.target.value))}
              className="w-full accent-cyan-500"
            />
          </div>
        </div>

        {/* Results Comparison Column */}
        <div className="lg:col-span-2 space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            {/* Monthly Impact */}
            <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-3">
              <span className="text-xs font-semibold text-slate-400 uppercase">Monthly Cash Flow Delta</span>
              <div className="text-3xl font-bold text-emerald-400">
                +${result?.impact.monthly_savings_increase?.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </div>
              <p className="text-xs text-slate-400">
                Simulated Net: <strong className="text-white">${result?.simulated.monthly_net_cashflow?.toLocaleString()}</strong> vs Baseline ${result?.baseline.monthly_net_cashflow?.toLocaleString()}
              </p>
            </div>

            {/* Annual Impact */}
            <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-3">
              <span className="text-xs font-semibold text-slate-400 uppercase">Annual Projected Surplus</span>
              <div className="text-3xl font-bold text-cyan-400">
                +${result?.impact.annual_savings_increase?.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </div>
              <p className="text-xs text-slate-400">Cumulative 12-month capital improvement</p>
            </div>
          </div>

          {/* Goal Acceleration Table */}
          {result?.impact.goal_accelerations?.length > 0 && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h2 className="text-base font-semibold text-white mb-3">Financial Goal Acceleration</h2>
              <div className="space-y-3">
                {result.impact.goal_accelerations.map((g: any) => (
                  <div key={g.goal_id} className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between text-xs">
                    <div>
                      <h3 className="font-semibold text-white">{g.title}</h3>
                      <p className="text-slate-400 mt-0.5">
                        Reduced completion timeline from {g.baseline_months_to_complete} months to {g.simulated_months_to_complete} months.
                      </p>
                    </div>
                    <span className="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-300 font-bold">
                      {g.months_saved} Months Saved
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
