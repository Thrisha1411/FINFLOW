import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, Lock, Mail, ArrowRight, UserCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('admin@finflow.ai');
  const [password, setPassword] = useState('Admin123!@#');
  const [totpCode, setTotpCode] = useState('');
  const [mfaRequired, setMfaRequired] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');
    try {
      const res = await login(email, password, totpCode || undefined);
      if (res && res.mfa_required) {
        setMfaRequired(true);
      } else {
        navigate('/');
      }
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Invalid email or password.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickDemo = (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setMfaRequired(false);
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-6 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>

      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl relative z-10 space-y-6">
        {/* Brand */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-indigo-600 to-cyan-400 mx-auto flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <ShieldCheck className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">FinFlow AI</h1>
          <p className="text-xs text-slate-400">
            Enterprise Financial Operations, Fraud Intelligence & Payment Automation
          </p>
        </div>

        {errorMsg && (
          <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Business Email</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-slate-950 border border-slate-750 rounded-lg pl-10 pr-4 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-slate-950 border border-slate-750 rounded-lg pl-10 pr-4 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          {mfaRequired && (
            <div>
              <label className="block text-xs font-medium text-cyan-400 mb-1">
                Two-Factor Authentication Code (TOTP)
              </label>
              <input
                type="text"
                required
                placeholder="6-digit code or recovery code"
                value={totpCode}
                onChange={(e) => setTotpCode(e.target.value)}
                className="w-full bg-slate-950 border border-cyan-500/50 rounded-lg px-3 py-2 text-sm text-white font-mono tracking-widest text-center focus:outline-none"
              />
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm shadow-md shadow-indigo-600/30 transition disabled:opacity-50"
          >
            <span>{loading ? 'Authenticating...' : mfaRequired ? 'Verify 2FA' : 'Sign In to Dashboard'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Demo Fast Login Switcher */}
        <div className="pt-4 border-t border-slate-800 space-y-2">
          <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider text-center">
            Demo Persona Quick Selection
          </p>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <button
              type="button"
              onClick={() => handleQuickDemo('admin@finflow.ai', 'Admin123!@#')}
              className="p-2 rounded bg-slate-950 border border-slate-800 hover:border-indigo-500 text-slate-300 transition text-left"
            >
              <div className="font-semibold text-white">Super Admin</div>
              <div className="text-[10px] text-slate-500">Alexander Wright</div>
            </button>
            <button
              type="button"
              onClick={() => handleQuickDemo('manager@finflow.ai', 'Manager123!@#')}
              className="p-2 rounded bg-slate-950 border border-slate-800 hover:border-indigo-500 text-slate-300 transition text-left"
            >
              <div className="font-semibold text-white">Finance Manager</div>
              <div className="text-[10px] text-slate-500">Sarah Jenkins</div>
            </button>
            <button
              type="button"
              onClick={() => handleQuickDemo('analyst@finflow.ai', 'Analyst123!@#')}
              className="p-2 rounded bg-slate-950 border border-slate-800 hover:border-indigo-500 text-slate-300 transition text-left"
            >
              <div className="font-semibold text-white">Financial Analyst</div>
              <div className="text-[10px] text-slate-500">David Chen</div>
            </button>
            <button
              type="button"
              onClick={() => handleQuickDemo('auditor@finflow.ai', 'Auditor123!@#')}
              className="p-2 rounded bg-slate-950 border border-slate-800 hover:border-indigo-500 text-slate-300 transition text-left"
            >
              <div className="font-semibold text-white">Auditor</div>
              <div className="text-[10px] text-slate-500">Elena Rostova</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
