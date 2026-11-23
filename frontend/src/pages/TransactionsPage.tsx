import React, { useEffect, useState } from 'react';
import { Plus, Search, Filter, CheckCircle, RotateCcw, AlertTriangle, ArrowUpDown } from 'lucide-react';
import api from '../api/client';
import type { Transaction } from '../types';

export const TransactionsPage: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [showModal, setShowModal] = useState(false);
  
  // New transaction form state
  const [formData, setFormData] = useState({
    merchant_name: '',
    amount: '',
    currency: 'USD',
    description: '',
    payment_method: 'CORPORATE_CARD'
  });
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const fetchTransactions = async () => {
    try {
      const params: any = {};
      if (search) params.search = search;
      if (statusFilter) params.status = statusFilter;
      const res = await api.get('/transactions', { params });
      setTransactions(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, [search, statusFilter]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setErrorMsg('');
    try {
      await api.post('/transactions', {
        merchant_name: formData.merchant_name,
        amount: parseFloat(formData.amount),
        currency: formData.currency,
        description: formData.description,
        payment_method: formData.payment_method
      });
      setShowModal(false);
      setFormData({
        merchant_name: '',
        amount: '',
        currency: 'USD',
        description: '',
        payment_method: 'CORPORATE_CARD'
      });
      fetchTransactions();
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to execute transaction.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleApprove = async (id: string) => {
    try {
      await api.post(`/transactions/${id}/approve`);
      fetchTransactions();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Approval failed.');
    }
  };

  const handleRefund = async (id: string, amount: number) => {
    const reason = prompt('Please enter the reason for this refund:');
    if (!reason) return;
    try {
      await api.post(`/transactions/${id}/refund`, {
        transaction_id: id,
        amount,
        reason
      });
      fetchTransactions();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Refund failed.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Payments & Transactions</h1>
          <p className="text-sm text-slate-400 mt-1">
            End-to-end payment lifecycle orchestration with real-time risk scoring and idempotency.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-semibold shadow-md shadow-indigo-600/30 transition"
        >
          <Plus className="w-4 h-4" />
          Initiate Transaction
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-4 rounded-xl">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search by merchant or reference ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-950 border border-slate-750 rounded-lg pl-10 pr-4 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-950 border border-slate-750 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Statuses</option>
            <option value="SUCCESS">Success</option>
            <option value="PENDING_APPROVAL">Pending Approval</option>
            <option value="FLAGGED">Flagged</option>
            <option value="REFUNDED">Refunded</option>
          </select>
        </div>
      </div>

      {/* Transactions Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/40 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                <th className="py-3 px-6">Reference ID</th>
                <th className="py-3 px-6">Merchant</th>
                <th className="py-3 px-6">Amount</th>
                <th className="py-3 px-6">Lifecycle Status</th>
                <th className="py-3 px-6">AI Risk Score</th>
                <th className="py-3 px-6">Method</th>
                <th className="py-3 px-6">Timestamp</th>
                <th className="py-3 px-6 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-sm">
              {transactions.map((tx) => {
                const isIncome = tx.amount < 0;
                return (
                  <tr key={tx.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-6 font-mono text-xs text-indigo-400 font-medium">{tx.reference_id}</td>
                    <td className="py-3.5 px-6">
                      <div className="font-semibold text-white">{tx.merchant_name}</div>
                      {tx.description && <div className="text-xs text-slate-400">{tx.description}</div>}
                    </td>
                    <td className={`py-3.5 px-6 font-bold ${isIncome ? 'text-emerald-400' : 'text-slate-100'}`}>
                      {isIncome ? `+$${Math.abs(tx.amount).toFixed(2)}` : `$${tx.amount.toFixed(2)}`}
                    </td>
                    <td className="py-3.5 px-6">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                          tx.status === 'SUCCESS'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : tx.status === 'FLAGGED'
                            ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                            : tx.status === 'PENDING_APPROVAL'
                            ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                            : 'bg-slate-700/50 text-slate-300'
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
                    <td className="py-3.5 px-6 text-xs text-slate-400 font-mono">{tx.payment_method}</td>
                    <td className="py-3.5 px-6 text-xs text-slate-400">
                      {new Date(tx.created_at).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-6 text-right space-x-2">
                      {tx.status === 'PENDING_APPROVAL' && (
                        <button
                          onClick={() => handleApprove(tx.id)}
                          className="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium rounded transition"
                        >
                          Approve
                        </button>
                      )}
                      {tx.status === 'SUCCESS' && tx.amount > 0 && (
                        <button
                          onClick={() => handleRefund(tx.id, tx.amount)}
                          className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded border border-slate-700 transition"
                        >
                          Refund
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Transaction Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 w-full max-w-md rounded-xl p-6 shadow-2xl">
            <h2 className="text-lg font-bold text-white mb-1">Simulate Payment Lifecycle</h2>
            <p className="text-xs text-slate-400 mb-4">
              Dispatches through AI risk evaluation, anomaly detection, and gateway orchestration.
            </p>

            {errorMsg && (
              <div className="mb-4 p-3 rounded bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs">
                {errorMsg}
              </div>
            )}

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Merchant / Payee Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Amazon Web Services, Starbucks"
                  value={formData.merchant_name}
                  onChange={(e) => setFormData({ ...formData, merchant_name: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Amount (USD)</label>
                <input
                  type="number"
                  step="0.01"
                  required
                  placeholder="e.g. 150.00"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Payment Method</label>
                <select
                  value={formData.payment_method}
                  onChange={(e) => setFormData({ ...formData, payment_method: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="CORPORATE_CARD">Corporate Visa / Mastercard</option>
                  <option value="ACH_TRANSFER">ACH Direct Debit</option>
                  <option value="WIRE_TRANSFER">Domestic / International Wire</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Description / Memo</label>
                <input
                  type="text"
                  placeholder="Optional expense memo"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-semibold transition"
                >
                  {submitting ? 'Orchestrating...' : 'Authorize & Process'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
