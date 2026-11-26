import { ReactNode } from "react";

export function Panel({ title, children, action }: { title: string; children: ReactNode; action?: ReactNode }) {
  return (
    <section className="rounded-md border border-white/10 bg-panel p-4 shadow-glow backdrop-blur-xl">
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300">{title}</h2>
        {action}
      </div>
      {children}
    </section>
  );
}

export function Metric({ label, value, tone = "text-mint" }: { label: string; value: string; tone?: string }) {
  return (
    <div className="rounded-md border border-white/10 bg-white/5 p-4">
      <div className="text-xs uppercase tracking-wider text-slate-400">{label}</div>
      <div className={`mt-2 text-2xl font-semibold ${tone}`}>{value}</div>
    </div>
  );
}

