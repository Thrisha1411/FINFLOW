import { Panel } from "../ui/Panel";

export function AuditLogs() {
  const logs = [
    ["approval.updated", "Transaction", "10:42"],
    ["login.suspicious", "Session", "10:18"],
    ["fraud.case.created", "FraudCase", "09:54"],
    ["budget.alert.triggered", "Budget", "09:31"]
  ];
  return (
    <Panel title="Searchable Audit Trail">
      <div className="divide-y divide-white/10">
        {logs.map(([action, resource, time]) => (
          <div key={action} className="grid grid-cols-[1fr_160px_80px] py-3 text-sm">
            <span className="font-medium text-slate-200">{action}</span>
            <span className="text-slate-400">{resource}</span>
            <span className="text-slate-400">{time}</span>
          </div>
        ))}
      </div>
    </Panel>
  );
}

