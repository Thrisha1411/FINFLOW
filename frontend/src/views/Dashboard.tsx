import { useQuery } from "@tanstack/react-query";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../api/client";
import { demoDashboard } from "../api/demoData";
import { Metric, Panel } from "../ui/Panel";
import { formatInr } from "../utils/format";

const spend = [
  { month: "Jan", value: 4020000 },
  { month: "Feb", value: 4260000 },
  { month: "Mar", value: 4130000 },
  { month: "Apr", value: 5180000 },
  { month: "May", value: 4880000 },
  { month: "Jun", value: 5635000 }
];

export function Dashboard() {
  const { data } = useQuery({
    queryKey: ["dashboard"],
    queryFn: async () => {
      try {
        return (await api.get("/analytics/dashboard")).data;
      } catch {
        return demoDashboard;
      }
    },
    retry: false
  });
  const dashboard = data ?? demoDashboard;
  const risks = dashboard.risk_distribution;
  return (
    <div className="space-y-5">
      <div className="grid gap-4 md:grid-cols-4">
        <Metric label="Revenue" value={formatInr(dashboard.revenue)} />
        <Metric label="Expenses" value={formatInr(dashboard.expenses)} tone="text-cyan" />
        <Metric label="Fraud Events" value={`${dashboard.fraud_events}`} tone="text-rose" />
        <Metric label="Budget Risk" value={dashboard.forecast.budget_risk} tone="text-amber" />
      </div>
      <div className="grid gap-5 xl:grid-cols-[1.4fr_0.8fr]">
        <Panel title="Cash Flow Forecast">
          <div className="h-80">
            <ResponsiveContainer>
              <AreaChart data={spend}>
                <CartesianGrid stroke="#ffffff16" />
                <XAxis dataKey="month" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ background: "#0b1518", border: "1px solid #ffffff22" }} />
                <Area type="monotone" dataKey="value" stroke="#54f0b2" fill="#54f0b233" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Risk Distribution">
          <div className="h-80">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={risks} dataKey="value" nameKey="name" innerRadius={72} outerRadius={110}>
                  {risks.map((_: unknown, index: number) => <Cell key={index} fill={["#54f0b2", "#f2b84b", "#f25f73"][index]} />)}
                </Pie>
                <Tooltip contentStyle={{ background: "#0b1518", border: "1px solid #ffffff22" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>
      <Panel title="Budget Performance">
        <div className="h-72">
          <ResponsiveContainer>
            <BarChart data={dashboard.budget_performance}>
              <CartesianGrid stroke="#ffffff16" />
              <XAxis dataKey="category" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ background: "#0b1518", border: "1px solid #ffffff22" }} />
              <Bar dataKey="used" fill="#66d9ef" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Panel>
    </div>
  );
}
