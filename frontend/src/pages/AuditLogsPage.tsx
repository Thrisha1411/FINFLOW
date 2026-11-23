import React, { useEffect, useState } from 'react';
import { FileText, Shield, Search } from 'lucide-react';
import api from '../api/client';
import type { AuditLog } from '../types';

export const AuditLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchLogs = async () => {
    try {
      const res = await api.get('/audit', { params: { action: search } });
      setLogs(res.data.items);
      setTotal(res.data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [search]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Compliance & Immutable Audit Ledger</h1>
        <p className="text-sm text-slate-400 mt-1">
          Cryptographically auditable append-only ledger tracking all authentication, payment, and approval actions.
        </p>
      </div>

      {/* Search Bar */}
      <div className="flex items-center bg-slate-900 border border-slate-800 p-3.5 rounded-xl max-w-md">
        <Search className="w-4 h-4 text-slate-400 mr-3" />
        <input
          type="text"
          placeholder="Filter by action (e.g. TRANSACTION, REFUND, USER)..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-transparent text-sm text-white placeholder-slate-500 focus:outline-none w-full"
        />
      </div>

      {/* Logs Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-indigo-400" />
            <h2 className="text-base font-semibold text-white">Verified Ledger ({total} Records)</h2>
          </div>
          <span className="text-xs text-slate-400">Append-Only • Restricted Deletion</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/40 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                <th className="py-3 px-6">Timestamp</th>
                <th className="py-3 px-6">Actor</th>
                <th className="py-3 px-6">Action Executed</th>
                <th className="py-3 px-6">Resource</th>
                <th className="py-3 px-6">Request ID</th>
                <th className="py-3 px-6">IP Address</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-xs">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-800/40 transition">
                  <td className="py-3 px-6 text-slate-400">{new Date(log.created_at).toLocaleString()}</td>
                  <td className="py-3 px-6 font-semibold text-white">{log.actor_email || log.actor_id}</td>
                  <td className="py-3 px-6">
                    <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-mono font-medium">
                      {log.action}
                    </span>
                  </td>
                  <td className="py-3 px-6 font-mono text-slate-300">{log.resource_type}</td>
                  <td className="py-3 px-6 font-mono text-slate-400">{log.request_id || 'N/A'}</td>
                  <td className="py-3 px-6 font-mono text-slate-400">{log.ip_address || '127.0.0.1'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
