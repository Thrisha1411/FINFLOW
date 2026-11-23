import React, { useState } from 'react';
import { ShieldCheck, Key, Lock, Copy, Check } from 'lucide-react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';

export const SettingsPage: React.FC = () => {
  const { user } = useAuth();
  const [setupData, setSetupData] = useState<any>(null);
  const [verifyCode, setVerifyCode] = useState('');
  const [success, setSuccess] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleStart2FA = async () => {
    try {
      const res = await api.post('/auth/2fa/setup');
      setSetupData(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleVerify2FA = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/auth/2fa/enable', { code: verifyCode });
      setSuccess(true);
      setSetupData(null);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Invalid verification code.');
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Security & Organization Settings</h1>
        <p className="text-sm text-slate-400 mt-1">
          Manage RFC 6238 TOTP two-factor authentication, team roles, and organization credentials.
        </p>
      </div>

      {/* Two-Factor Authentication (TOTP) Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-indigo-500/10 text-indigo-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-white">Two-Factor Authentication (TOTP)</h2>
              <p className="text-xs text-slate-400">
                Secure your account with Google Authenticator, Microsoft Authenticator, or 1Password.
              </p>
            </div>
          </div>
          <span
            className={`px-3 py-1 rounded-full text-xs font-semibold ${
              user?.is_totp_enabled || success
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
            }`}
          >
            {user?.is_totp_enabled || success ? 'Enabled' : 'Disabled'}
          </span>
        </div>

        {!user?.is_totp_enabled && !success && (
          <div>
            {!setupData ? (
              <button
                onClick={handleStart2FA}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-semibold transition"
              >
                Configure Authenticator App
              </button>
            ) : (
              <div className="space-y-4 pt-2">
                <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
                  <div className="text-xs font-medium text-slate-300">Base32 Secret Key:</div>
                  <div className="flex items-center gap-3 font-mono text-sm text-indigo-400 font-bold">
                    <span>{setupData.secret}</span>
                    <button
                      onClick={() => copyToClipboard(setupData.secret)}
                      className="p-1 text-slate-400 hover:text-white"
                      title="Copy Secret"
                    >
                      {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                    </button>
                  </div>
                  <p className="text-[11px] text-slate-400">
                    Or copy the provisioning URI into your authenticator app:
                  </p>
                  <div className="text-[10px] text-slate-500 break-all font-mono">
                    {setupData.provisioning_uri}
                  </div>
                </div>

                <form onSubmit={handleVerify2FA} className="flex items-center gap-3">
                  <input
                    type="text"
                    required
                    placeholder="Enter 6-digit code..."
                    value={verifyCode}
                    onChange={(e) => setVerifyCode(e.target.value)}
                    className="bg-slate-950 border border-slate-750 rounded-lg px-3 py-2 text-sm text-white w-48 font-mono tracking-widest text-center focus:outline-none focus:border-indigo-500"
                  />
                  <button
                    type="submit"
                    className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-semibold transition"
                  >
                    Verify & Enable
                  </button>
                </form>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Organization Info */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
        <h2 className="text-base font-semibold text-white">Active Organization Profile</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-xs text-slate-400">Organization Name</span>
            <div className="font-semibold text-white mt-1">Acme Financial Corp</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-xs text-slate-400">Base Currency</span>
            <div className="font-semibold text-white mt-1">USD ($)</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-xs text-slate-400">Your Current Role</span>
            <div className="font-semibold text-indigo-400 mt-1">{user?.role}</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-xs text-slate-400">Multi-Tenant Isolation</span>
            <div className="font-semibold text-emerald-400 mt-1">Active & Enforced</div>
          </div>
        </div>
      </div>
    </div>
  );
};
