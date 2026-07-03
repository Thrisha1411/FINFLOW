import { useMutation } from "@tanstack/react-query";
import { CheckCircle2, Plus, RotateCcw } from "lucide-react";
import { useState } from "react";
import { demoTransactions } from "../api/demoData";
import { Panel } from "../ui/Panel";
import { formatInr } from "../utils/format";

export function Transactions() {
  const [localRows, setLocalRows] = useState(demoTransactions);
  const [merchant, setMerchant] = useState("Vendor Payment");
  const [amount, setAmount] = useState("25000");
  const [message, setMessage] = useState("");
  const create = useMutation({
    mutationFn: async () => {
      const payload = { merchant, amount: Number(amount), currency: "INR" };
      if (!payload.merchant.trim() || !Number.isFinite(payload.amount) || payload.amount <= 0) {
        throw new Error("Enter a merchant and a valid INR amount.");
      }
      const score = payload.amount > 500000 ? 88 : payload.amount > 100000 ? 46 : 18;
      const row = {
        id: crypto.randomUUID(),
        ...payload,
        status: score > 75 ? "FLAGGED" : score > 40 ? "APPROVAL" : "PROCESSING",
        risk_score: score
      };
      setLocalRows((rows) => [row, ...rows]);
      setMessage(`${payload.merchant} added for ${formatInr(payload.amount)}.`);
      return row;
    }
  });
  const rows = localRows;
  return (
    <Panel title="Payment Workflow Engine" action={<span className="rounded-md bg-white/5 px-3 py-2 text-xs text-slate-300">Currency: INR</span>}>
      <form
        onSubmit={(event) => {
          event.preventDefault();
          create.mutate();
        }}
        className="mb-5 grid gap-3 rounded-md border border-white/10 bg-black/20 p-3 md:grid-cols-[1fr_180px_auto]"
      >
        <input value={merchant} onChange={(event) => setMerchant(event.target.value)} placeholder="Merchant" className="rounded-md border border-white/10 bg-white/5 px-3 py-2 text-sm outline-none focus:border-mint" />
        <input value={amount} onChange={(event) => setAmount(event.target.value)} type="number" min="1" placeholder="Amount in INR" className="rounded-md border border-white/10 bg-white/5 px-3 py-2 text-sm outline-none focus:border-mint" />
        <button disabled={create.isPending} className="inline-flex items-center justify-center gap-2 rounded-md bg-mint px-3 py-2 text-sm font-semibold text-ink disabled:opacity-60">
          <Plus className="h-4 w-4" />Create
        </button>
      </form>
      {message && <div className="mb-4 flex items-center gap-2 rounded-md border border-mint/30 bg-mint/10 px-3 py-2 text-sm text-mint"><CheckCircle2 className="h-4 w-4" />{message}</div>}
      {create.isError && <div className="mb-4 rounded-md border border-rose/30 bg-rose/10 px-3 py-2 text-sm text-rose">{(create.error as Error).message}</div>}
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="text-xs uppercase tracking-wider text-slate-400">
            <tr><th className="py-3">Merchant</th><th>Amount</th><th>Status</th><th>Risk</th><th>Action</th></tr>
          </thead>
          <tbody className="divide-y divide-white/10">
            {rows.map((row: any, index: number) => (
              <tr key={row.id ?? index} className="text-slate-200">
                <td className="py-3 font-medium">{row.merchant}</td>
                <td>{formatInr(row.amount)}</td>
                <td><span className="rounded-md border border-white/10 bg-white/5 px-2 py-1 text-xs">{row.status}</span></td>
                <td className={row.risk_score > 75 ? "text-rose" : "text-mint"}>{row.risk_score}</td>
                <td><button className="rounded-md p-2 hover:bg-white/10" title="Retry payment"><RotateCcw className="h-4 w-4" /></button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Panel>
  );
}
