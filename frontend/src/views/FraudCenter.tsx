import { useState } from "react";
import { ShieldCheck, TriangleAlert } from "lucide-react";
import { demoFraudDecision } from "../api/demoData";
import { Panel } from "../ui/Panel";
import { formatInr } from "../utils/format";

export function FraudCenter() {
  const [decision, setDecision] = useState(demoFraudDecision);
  const [lastScan, setLastScan] = useState("Ready to scan");

  function runScan() {
    const amount = 980000;
    const priorCount = 6;
    const priorAmount = 1800000;
    const riskScore = Math.min(98, Math.round(amount / 18000 + priorCount * 5 + priorAmount / 90000));
    setDecision({
      risk_score: riskScore,
      fraud_reason: `Velocity=${priorCount} tx/day, amount=INR ${amount.toLocaleString("en-IN")}, unfamiliar payment pattern`,
      recommendation: riskScore >= 75 ? "Hold for finance manager approval and request second-factor verification." : "Route to analyst queue before processing."
    });
    setLastScan(`Scan completed for ${formatInr(amount)}`);
  }

  return (
    <div className="grid gap-5 lg:grid-cols-[0.8fr_1.2fr]">
      <Panel title="Live Fraud Score" action={<button onClick={runScan} className="rounded-md bg-mint px-3 py-2 text-sm font-semibold text-ink">Run Scan</button>}>
        <div className="flex items-center gap-5">
          <div className="grid h-24 w-24 place-items-center rounded-md border border-rose/30 bg-rose/10">
            <TriangleAlert className="h-10 w-10 text-rose" />
          </div>
          <div>
            <div className="text-4xl font-semibold text-rose">{decision.risk_score}</div>
            <div className="mt-2 text-slate-300">{decision.fraud_reason}</div>
            <div className="mt-1 text-sm text-slate-400">Sample amount: {formatInr(980000)}</div>
            <div className="mt-2 text-sm text-mint">{lastScan}</div>
          </div>
        </div>
      </Panel>
      <Panel title="Investigation Recommendation">
        <div className="flex gap-4">
          <ShieldCheck className="mt-1 h-5 w-5 text-mint" />
          <p className="text-slate-300">{decision.recommendation}</p>
        </div>
      </Panel>
    </div>
  );
}
