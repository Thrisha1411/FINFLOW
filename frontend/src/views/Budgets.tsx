import { useMemo, useState } from "react";
import { AlertTriangle, Brain, IndianRupee, LucideIcon, ShieldCheck, Target, TrendingUp } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Cell, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { budgetProfiles, budgetSpending, budgetTrend, subscriptionImpact } from "../api/demoData";
import { Metric, Panel } from "../ui/Panel";
import { formatInr } from "../utils/format";

type Profile = keyof typeof budgetProfiles;

const incomePresets: Record<Profile, number> = {
  Student: 35000,
  "Working Professional": 60000,
  Freelancer: 85000,
  Family: 120000,
  "Business Owner": 250000,
  "High Income User": 300000
};

const goals: Array<{ name: string; targetAmount: number; currentAmount: number; Icon: LucideIcon }> = [
  { name: "Emergency fund", targetAmount: 180000, currentAmount: 64200, Icon: Target },
  { name: "Mutual fund SIP", targetAmount: 120000, currentAmount: 76000, Icon: IndianRupee },
  { name: "Debt reduction", targetAmount: 90000, currentAmount: 38000, Icon: TrendingUp }
];

function sumBy(group: string) {
  return budgetSpending.filter((item) => item.group === group).reduce((sum, item) => sum + item.amount, 0);
}

function scoreLabel(score: number) {
  if (score >= 90) return "Excellent";
  if (score >= 75) return "Good";
  if (score >= 60) return "Average";
  return "Needs Improvement";
}

export function Budgets() {
  const [profile, setProfile] = useState<Profile>("Working Professional");
  const [income, setIncome] = useState(incomePresets["Working Professional"]);
  const target = budgetProfiles[profile];
  const grouped = useMemo(() => ({
    Needs: sumBy("Needs"),
    Wants: sumBy("Wants"),
    Savings: sumBy("Savings")
  }), []);
  const current = {
    Needs: Math.round((grouped.Needs / income) * 100),
    Wants: Math.round((grouped.Wants / income) * 100),
    Savings: Math.round((grouped.Savings / income) * 100)
  };
  const deviation = {
    Needs: current.Needs - target.Needs,
    Wants: current.Wants - target.Wants,
    Savings: current.Savings - target.Savings
  };
  const adherencePenalty = Math.abs(deviation.Needs) + Math.abs(deviation.Wants) + Math.abs(deviation.Savings);
  const subscriptionPenalty = subscriptionImpact.filter((item) => item.risk !== "Healthy").length * 4;
  const healthScore = Math.max(0, Math.min(100, Math.round(84 + (current.Savings - target.Savings) * 1.4 - adherencePenalty * 0.55 - subscriptionPenalty)));
  const monthlySavingsOpportunity = 3500 + (subscriptionImpact.find((item) => item.risk === "Unused")?.amount ?? 0);
  const nextMonth = {
    Needs: Math.round(income * target.Needs / 100),
    Wants: Math.round(income * target.Wants / 100),
    Savings: Math.round(income * target.Savings / 100)
  };
  const breakdown = [
    { name: "Needs", actual: current.Needs, target: target.Needs, amount: grouped.Needs },
    { name: "Wants", actual: current.Wants, target: target.Wants, amount: grouped.Wants },
    { name: "Savings", actual: current.Savings, target: target.Savings, amount: grouped.Savings }
  ];
  const forecast = [
    { category: "Needs", current: grouped.Needs, forecast: nextMonth.Needs },
    { category: "Wants", current: grouped.Wants, forecast: nextMonth.Wants },
    { category: "Savings", current: grouped.Savings, forecast: nextMonth.Savings }
  ];
  const alerts = [
    deviation.Needs > 8 ? "Budget limit approaching: needs are above profile target." : "Needs spending is under watch.",
    "Overspending prediction: dining may rise 15% next month.",
    current.Savings < target.Savings ? "Savings target missed for this month." : "Savings target is on track.",
    "Subscription increase detected for Cloud Storage.",
    "Unusual transportation spending spike detected."
  ];

  function changeProfile(nextProfile: Profile) {
    setProfile(nextProfile);
    setIncome(incomePresets[nextProfile]);
  }

  return (
    <div className="space-y-5">
      <div className="grid gap-4 md:grid-cols-4">
        <Metric label="Budget Health" value={`${healthScore}`} tone={healthScore >= 75 ? "text-mint" : "text-amber"} />
        <Metric label="Health Label" value={scoreLabel(healthScore)} tone="text-cyan" />
        <Metric label="Savings Opportunity" value={formatInr(monthlySavingsOpportunity)} tone="text-mint" />
        <Metric label="Next Month Target" value={formatInr(nextMonth.Savings)} tone="text-amber" />
      </div>

      <Panel
        title="Adaptive Budget Planning"
        action={
          <div className="flex flex-wrap items-center gap-2">
            <select value={profile} onChange={(event) => changeProfile(event.target.value as Profile)} className="rounded-md border border-white/10 bg-ink px-3 py-2 text-sm outline-none focus:border-mint">
              {Object.keys(budgetProfiles).map((item) => <option key={item}>{item}</option>)}
            </select>
            <input value={income} onChange={(event) => setIncome(Number(event.target.value))} type="number" min="1" className="w-32 rounded-md border border-white/10 bg-ink px-3 py-2 text-sm outline-none focus:border-mint" />
          </div>
        }
      >
        <div className="grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="rounded-md border border-white/10 bg-white/5 p-4">
            <div className="mb-4 flex items-center gap-3">
              <div className="grid h-12 w-12 place-items-center rounded-md border border-mint/30 bg-mint/10">
                <ShieldCheck className="h-6 w-6 text-mint" />
              </div>
              <div>
                <div className="text-lg font-semibold">{scoreLabel(healthScore)} financial health</div>
                <div className="text-sm text-slate-400">Income {formatInr(income)} with {profile} allocation</div>
              </div>
            </div>
            <div className="space-y-3">
              {breakdown.map((item) => (
                <div key={item.name}>
                  <div className="flex justify-between text-sm">
                    <span>{item.name}</span>
                    <span className={item.actual > item.target ? "text-amber" : "text-mint"}>{item.actual}% actual / {item.target}% target</span>
                  </div>
                  <div className="mt-2 h-3 rounded-md bg-white/10">
                    <div className="h-3 rounded-md bg-mint" style={{ width: `${Math.min(100, item.actual)}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="h-80">
            <ResponsiveContainer>
              <BarChart data={breakdown}>
                <CartesianGrid stroke="#ffffff16" />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ background: "#0b1518", border: "1px solid #ffffff22" }} />
                <Bar dataKey="target" fill="#66d9ef" radius={[4, 4, 0, 0]} />
                <Bar dataKey="actual" fill="#54f0b2" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </Panel>

      <div className="grid gap-5 xl:grid-cols-[1fr_1fr]">
        <Panel title="50/30/20 Breakdown">
          <div className="grid gap-4 md:grid-cols-[220px_1fr]">
            <div className="h-56">
              <ResponsiveContainer>
                <PieChart>
                  <Pie data={breakdown} dataKey="actual" nameKey="name" innerRadius={54} outerRadius={86}>
                    {breakdown.map((_, index) => <Cell key={index} fill={["#54f0b2", "#66d9ef", "#f2b84b"][index]} />)}
                  </Pie>
                  <Tooltip contentStyle={{ background: "#0b1518", border: "1px solid #ffffff22" }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="space-y-3 text-sm text-slate-300">
              <div>Needs exceed the recommended allocation by {Math.max(0, deviation.Needs)}%.</div>
              <div>Wants are {deviation.Wants > 0 ? `${deviation.Wants}% above` : `${Math.abs(deviation.Wants)}% below`} profile target.</div>
              <div>Savings are {deviation.Savings < 0 ? `${Math.abs(deviation.Savings)}% below` : `${deviation.Savings}% above`} target.</div>
              <div className="rounded-md border border-amber/30 bg-amber/10 p-3 text-amber">AI Insight: Reducing transportation, utilities, and unused subscriptions could increase monthly savings.</div>
            </div>
          </div>
        </Panel>

        <Panel title="Next Month Forecast">
          <div className="space-y-3">
            {forecast.map((item) => (
              <div key={item.category} className="rounded-md border border-white/10 bg-white/5 p-3">
                <div className="flex items-center justify-between text-sm">
                  <span>{item.category}</span>
                  <span>{formatInr(item.forecast)}</span>
                </div>
                <div className="mt-2 text-xs text-slate-400">Current {formatInr(item.current)} compared with recommended next month limit.</div>
              </div>
            ))}
            <div className="rounded-md border border-rose/30 bg-rose/10 p-3 text-sm text-rose">Predicted Risk: Food & Dining +15%</div>
          </div>
        </Panel>
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
        <Panel title="Spending Trend Graph">
          <div className="h-80">
            <ResponsiveContainer>
              <LineChart data={budgetTrend}>
                <CartesianGrid stroke="#ffffff16" />
                <XAxis dataKey="month" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ background: "#0b1518", border: "1px solid #ffffff22" }} />
                <Line type="monotone" dataKey="needs" stroke="#54f0b2" strokeWidth={2} />
                <Line type="monotone" dataKey="wants" stroke="#66d9ef" strokeWidth={2} />
                <Line type="monotone" dataKey="savings" stroke="#f2b84b" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel title="Subscription Impact">
          <div className="space-y-3">
            {subscriptionImpact.map((item) => (
              <div key={item.merchant} className="flex items-center justify-between rounded-md border border-white/10 bg-white/5 p-3 text-sm">
                <div>
                  <div className="font-medium">{item.merchant}</div>
                  <div className={item.risk === "Healthy" ? "text-mint" : "text-amber"}>{item.risk}</div>
                </div>
                <div>{formatInr(item.amount)}</div>
              </div>
            ))}
          </div>
        </Panel>
      </div>

      <div className="grid gap-5 xl:grid-cols-[1fr_1fr]">
        <Panel title="AI Insights">
          <div className="space-y-3">
            {[
              "Dining expenses increased 18% compared to last month.",
              "Your savings rate improved by 7%.",
              "You are likely to exceed entertainment budget within 10 days.",
              `Current spending pattern may reduce annual savings by ${formatInr(42000)}.`
            ].map((item) => (
              <div key={item} className="flex gap-3 rounded-md border border-white/10 bg-white/5 p-3 text-sm text-slate-300">
                <Brain className="mt-0.5 h-4 w-4 shrink-0 text-mint" />
                {item}
              </div>
            ))}
          </div>
        </Panel>

        <Panel title="Budget Alerts">
          <div className="space-y-3">
            {alerts.map((item, index) => (
              <div key={item} className="flex gap-3 rounded-md border border-white/10 bg-white/5 p-3 text-sm text-slate-300">
                {index < 2 ? <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-rose" /> : <TrendingUp className="mt-0.5 h-4 w-4 shrink-0 text-amber" />}
                {item}
              </div>
            ))}
          </div>
        </Panel>
      </div>

      <Panel title="Financial Goals">
        <div className="grid gap-3 md:grid-cols-3">
          {goals.map(({ name, targetAmount, currentAmount, Icon }) => (
            <div key={name} className="rounded-md border border-white/10 bg-white/5 p-4">
              <Icon className="mb-3 h-5 w-5 text-mint" />
              <div className="font-semibold">{name}</div>
              <div className="mt-2 text-sm text-slate-400">{formatInr(currentAmount)} of {formatInr(targetAmount)}</div>
              <div className="mt-3 h-3 rounded-md bg-white/10">
                <div className="h-3 rounded-md bg-mint" style={{ width: `${Math.round(currentAmount / targetAmount * 100)}%` }} />
              </div>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  );
}
