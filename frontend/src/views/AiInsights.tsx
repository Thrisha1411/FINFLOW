import { useState } from "react";
import { Send } from "lucide-react";
import { Panel } from "../ui/Panel";
import { buildFinancialInsight, InsightResponse } from "../utils/insightEngine";

export function AiInsights() {
  const [question, setQuestion] = useState("Why was the large INR transfer flagged?");
  const [memory, setMemory] = useState("");
  const [insight, setInsight] = useState<InsightResponse | null>(null);

  function ask() {
    const response = buildFinancialInsight(question, memory);
    setInsight(response);
    setMemory(response.memory);
  }

  return (
    <Panel title="AI Financial Operations Assistant">
      <div className="grid gap-4">
        <div className="rounded-md border border-white/10 bg-black/20 p-4 text-slate-300">
          {insight?.answer ?? "Ask about budget analysis, flagged transactions, forecasts, subscriptions, savings optimization, or failed payments."}
        </div>
        {insight && (
          <div className="grid gap-3 lg:grid-cols-3">
            <div className="rounded-md border border-white/10 bg-white/5 p-3">
              <div className="text-xs uppercase tracking-wider text-slate-400">Intent</div>
              <div className="mt-2 text-sm text-mint">{insight.intent}</div>
            </div>
            <div className="rounded-md border border-white/10 bg-white/5 p-3">
              <div className="text-xs uppercase tracking-wider text-slate-400">Confidence</div>
              <div className="mt-2 text-sm text-cyan">{insight.confidence}%</div>
            </div>
            <div className="rounded-md border border-white/10 bg-white/5 p-3">
              <div className="text-xs uppercase tracking-wider text-slate-400">Recommended Action</div>
              <div className="mt-2 text-sm text-slate-300">{insight.action}</div>
            </div>
            <div className="rounded-md border border-white/10 bg-white/5 p-3 lg:col-span-3">
              <div className="text-xs uppercase tracking-wider text-slate-400">Reasoning</div>
              <div className="mt-2 text-sm text-slate-300">{insight.reasoning}</div>
            </div>
            <div className="rounded-md border border-white/10 bg-white/5 p-3 lg:col-span-3">
              <div className="text-xs uppercase tracking-wider text-slate-400">Supporting Evidence</div>
              <div className="mt-2 flex flex-wrap gap-2">
                {insight.evidence.map((item) => <span key={item} className="rounded-md bg-black/25 px-2 py-1 text-xs text-slate-300">{item}</span>)}
              </div>
            </div>
          </div>
        )}
        <div className="flex gap-2">
          <input value={question} onChange={(event) => setQuestion(event.target.value)} className="min-w-0 flex-1 rounded-md border border-white/10 bg-white/5 px-3 py-2 text-slate-100 outline-none focus:border-mint" />
          <button onClick={ask} className="grid h-10 w-10 place-items-center rounded-md bg-mint text-ink" title="Send question"><Send className="h-4 w-4" /></button>
        </div>
      </div>
    </Panel>
  );
}
