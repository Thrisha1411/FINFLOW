import { NavLink, Outlet } from "react-router-dom";
import { Bell, Bot, ChartNoAxesCombined, CreditCard, FileSearch, Gauge, IndianRupee, Landmark, Settings as SettingsIcon, ShieldAlert, WalletCards } from "lucide-react";
import { useEffect, useState } from "react";

const nav = [
  ["Dashboard", "/dashboard", Gauge],
  ["Transactions", "/transactions", CreditCard],
  ["Fraud Center", "/fraud", ShieldAlert],
  ["AI Insights", "/insights", Bot],
  ["Subscriptions", "/subscriptions", WalletCards],
  ["Budgets", "/budgets", ChartNoAxesCombined],
  ["Audit Logs", "/audit", FileSearch],
  ["Settings", "/settings", SettingsIcon]
] as const;

export default function AppShell() {
  const [pulse, setPulse] = useState("Demo workspace ready");
  useEffect(() => {
    try {
      const ws = new WebSocket(`${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws`);
      ws.onmessage = (event) => setPulse(JSON.parse(event.data).type ?? "Realtime update");
      ws.onopen = () => {
        setPulse("Live risk stream connected");
        ws.send(JSON.stringify({ type: "dashboard_subscribe" }));
      };
      ws.onerror = () => setPulse("Offline demo mode");
      return () => ws.close();
    } catch {
      setPulse("Offline demo mode");
    }
  }, []);

  return (
    <div className="min-h-screen bg-ink text-slate-100">
      <div className="fixed inset-0 bg-[radial-gradient(circle_at_top_left,rgba(84,240,178,0.13),transparent_28%),linear-gradient(135deg,#071013,#0e1b20_52%,#121719)]" />
      <div className="relative grid min-h-screen grid-cols-1 lg:grid-cols-[264px_1fr]">
        <aside className="border-r border-white/10 bg-black/25 px-4 py-5 backdrop-blur-xl">
          <div className="mb-8 flex items-center gap-3 px-2">
            <div className="grid h-10 w-10 place-items-center rounded-md border border-mint/30 bg-mint/10">
              <Landmark className="h-5 w-5 text-mint" />
            </div>
            <div>
              <div className="text-lg font-semibold tracking-normal">FinFlow AI</div>
              <div className="text-xs text-slate-400">India Finance Ops</div>
            </div>
          </div>
          <nav className="space-y-1">
            {nav.map(([label, path, Icon]) => (
              <NavLink key={path} to={path} className={({ isActive }) => `flex items-center gap-3 rounded-md px-3 py-2 text-sm transition ${isActive ? "bg-mint/15 text-mint" : "text-slate-300 hover:bg-white/10 hover:text-white"}`}>
                <Icon className="h-4 w-4" />
                {label}
              </NavLink>
            ))}
          </nav>
        </aside>
        <main className="min-w-0">
          <header className="sticky top-0 z-10 flex items-center justify-between border-b border-white/10 bg-ink/80 px-5 py-4 backdrop-blur-xl">
            <div>
              <div className="text-sm text-slate-400">Operations Command Center</div>
              <div className="text-xl font-semibold">INR workflows, fraud intelligence, and payment automation</div>
            </div>
            <div className="hidden items-center gap-2 rounded-md border border-mint/30 bg-mint/10 px-3 py-2 text-sm text-mint md:flex">
              <IndianRupee className="h-4 w-4" />
              Indian Rupees
            </div>
            <div className="flex items-center gap-3 rounded-md border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-300">
              <Bell className="h-4 w-4 text-amber" />
              {pulse}
            </div>
          </header>
          <section className="p-5">
            <Outlet />
          </section>
        </main>
      </div>
    </div>
  );
}
