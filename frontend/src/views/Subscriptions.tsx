import { Panel } from "../ui/Panel";
import { formatInr } from "../utils/format";

const subscriptions = [
  ["AWS India", 153000, "4 days", "Price increase"],
  ["Notion", 8000, "12 days", "Unused"],
  ["Slack", 35000, "18 days", "Healthy"]
];

export function Subscriptions() {
  return (
    <Panel title="Subscription Manager">
      <div className="grid gap-3 md:grid-cols-3">
        {subscriptions.map(([merchant, amount, renewal, signal]) => (
          <article key={merchant} className="rounded-md border border-white/10 bg-white/5 p-4">
            <div className="text-lg font-semibold">{merchant}</div>
            <div className="mt-3 text-2xl text-cyan">{formatInr(amount)}</div>
            <div className="mt-2 text-sm text-slate-400">Renews in {renewal}</div>
            <div className="mt-4 rounded-md bg-black/25 px-2 py-1 text-sm text-amber">{signal}</div>
          </article>
        ))}
      </div>
    </Panel>
  );
}
