import { Panel } from "../ui/Panel";

export function Settings() {
  return (
    <Panel title="Enterprise Security Settings">
      <div className="grid gap-4 md:grid-cols-2">
        {["Two-factor authentication", "Device trust enforcement", "IP anomaly detection", "Approval-chain segregation"].map((item) => (
          <label key={item} className="flex items-center justify-between rounded-md border border-white/10 bg-white/5 p-4">
            <span>{item}</span>
            <input type="checkbox" defaultChecked className="h-5 w-5 accent-mint" />
          </label>
        ))}
      </div>
    </Panel>
  );
}

