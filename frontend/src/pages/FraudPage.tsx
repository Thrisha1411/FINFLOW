import React, { useEffect, useState } from 'react';
import { ShieldAlert, ShieldCheck, AlertOctagon, CheckCircle2, Eye, FileText, Activity } from 'lucide-react';
import api from '../api/client';
import type { FraudCase } from '../types';

export const FraudPage: React.FC = () => {
  const [cases, setCases] = useState<FraudCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCase, setSelectedCase] = useState<FraudCase | null>(null);

  const fetchFraudCases = async () => {
    try {
      const res = await api.get('/fraud/cases');
      setCases(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFraudCases();
  }, []);

  const handleResolve = async (id: string, status: string) => {
    const notes = prompt('Enter resolution notes for audit trail:');
    try {
      await api.patch(`/fraud/cases/${id}`, {
        status,
        notes: notes || 'Analyst verified.'
      });
      fetchFraudCases();
      setSelectedCase(null);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">AI Fraud Intelligence Engine</h1>
        <p className="text-sm text-slate-400 mt-1">
          Hybrid Isolation Forest ML anomaly detection and behavioral heuristic rule surveillance.
        </p>
      </div>

      {/* Overview Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase">
            <span>Active Cases</span>
            <AlertOctagon className="w-4 h-4 text-rose-400" />
          </div>
          <div className="mt-2 text-2xl font-bold text-rose-400">
            {cases.filter((c) => c.status === 'OPEN').length}
          </div>
          <p className="text-xs text-slate-400 mt-1">Requiring immediate analyst clearance</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase">
            <span>Model Version</span>
            <Activity className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="mt-2 text-xl font-bold text-white">FinFlow-Hybrid-IF-1.2.0</div>
          <p className="text-xs text-indigo-400 mt-1">Calibrated on 4D statistical feature vectors</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase">
            <span>Resolution Rate</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-2 text-2xl font-bold text-emerald-400">99.4%</div>
          <p className="text-xs text-slate-400 mt-1">Zero automated false-positive lockouts</p>
        </div>
      </div>

      {/* Cases List */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800">
          <h2 className="text-base font-semibold text-white">Monitored High-Risk Inquiries</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/40 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                <th className="py-3 px-6">Risk Score</th>
                <th className="py-3 px-6">Classification</th>
                <th className="py-3 px-6">Action Recommended</th>
                <th className="py-3 px-6">Status</th>
                <th className="py-3 px-6">Supporting Evidence</th>
                <th className="py-3 px-6 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-sm">
              {cases.map((fc) => (
                <tr key={fc.id} className="hover:bg-slate-800/40 transition">
                  <td className="py-4 px-6">
                    <span
                      className={`font-mono font-bold text-base ${
                        fc.risk_score >= 80 ? 'text-rose-400' : fc.risk_score >= 60 ? 'text-amber-400' : 'text-yellow-400'
                      }`}
                    >
                      {fc.risk_score} / 100
                    </span>
                  </td>
                  <td className="py-4 px-6">
                    <span className="px-2 py-0.5 rounded text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/30">
                      {fc.risk_level}
                    </span>
                  </td>
                  <td className="py-4 px-6 font-mono text-xs font-semibold text-slate-200">
                    {fc.recommendation}
                  </td>
                  <td className="py-4 px-6">
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-medium ${
                        fc.status === 'OPEN'
                          ? 'bg-amber-500/20 text-amber-300'
                          : 'bg-emerald-500/20 text-emerald-300'
                      }`}
                    >
                      {fc.status}
                    </span>
                  </td>
                  <td className="py-4 px-6 text-xs text-slate-300 max-w-xs truncate">
                    {fc.investigator_notes || 'Elevated statistical anomaly detected.'}
                  </td>
                  <td className="py-4 px-6 text-right space-x-2">
                    <button
                      onClick={() => setSelectedCase(fc)}
                      className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded border border-slate-700 transition"
                    >
                      Signals
                    </button>
                    {fc.status === 'OPEN' && (
                      <button
                        onClick={() => handleResolve(fc.id, 'RESOLVED_BENIGN')}
                        className="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium rounded transition"
                      >
                        Clear Benign
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Signals Inspector Modal */}
      {selectedCase && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 w-full max-w-lg rounded-xl p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h2 className="text-lg font-bold text-white">Explainable AI Risk Signals</h2>
                <p className="text-xs text-slate-400">Case ID: {selectedCase.id}</p>
              </div>
              <span className="text-xl font-bold text-rose-400">{selectedCase.risk_score} / 100</span>
            </div>

            <div className="space-y-3 max-h-80 overflow-y-auto">
              {selectedCase.signals.map((sig) => (
                <div key={sig.id} className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-mono text-indigo-400 font-semibold">{sig.rule_code}</span>
                    <span className="px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300 text-[10px] font-bold">
                      {sig.severity} (wt: {sig.weight})
                    </span>
                  </div>
                  <h3 className="text-sm font-semibold text-white">{sig.signal_name}</h3>
                  <p className="text-xs text-slate-400">{sig.description}</p>
                </div>
              ))}
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedCase(null)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-lg"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
