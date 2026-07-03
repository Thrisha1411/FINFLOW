export const demoDashboard = {
  revenue: 10680000,
  expenses: 5635000,
  fraud_events: 18,
  forecast: { future_spending: 6120000, cash_flow_projection: -6120000, budget_risk: "Medium" },
  risk_distribution: [
    { name: "Low", value: 63 },
    { name: "Medium", value: 24 },
    { name: "High", value: 13 }
  ],
  budget_performance: [
    { category: "Travel", used: 72 },
    { category: "SaaS", used: 54 },
    { category: "Utilities", used: 41 }
  ]
};

export const demoTransactions = [
  { id: "t1", merchant: "AWS India", amount: 153000, currency: "INR", status: "APPROVAL", risk_score: 42 },
  { id: "t2", merchant: "High Value IMPS", amount: 1030000, currency: "INR", status: "FLAGGED", risk_score: 91 },
  { id: "t3", merchant: "Razorpay Settlement", amount: 515000, currency: "INR", status: "SUCCESS", risk_score: 12 },
  { id: "t4", merchant: "Tata Power", amount: 18400, currency: "INR", status: "PROCESSING", risk_score: 21 }
];

export const demoFraudDecision = {
  risk_score: 91,
  fraud_reason: "Velocity spike, unfamiliar device, and high-value INR transfer",
  recommendation: "Hold for finance manager approval and request second-factor verification."
};

export const demoAssistantAnswer =
  "The transaction was flagged because the amount is much higher than the account's usual INR payment range, multiple transfers happened within 24 hours, and the device is not yet trusted.";

export const budgetProfiles = {
  Student: { Needs: 60, Wants: 20, Savings: 20 },
  "Working Professional": { Needs: 50, Wants: 30, Savings: 20 },
  Freelancer: { Needs: 45, Wants: 25, Savings: 30 },
  Family: { Needs: 55, Wants: 25, Savings: 20 },
  "Business Owner": { Needs: 40, Wants: 30, Savings: 30 },
  "High Income User": { Needs: 40, Wants: 30, Savings: 30 }
} as const;

export const budgetSpending = [
  { category: "Rent", group: "Needs", amount: 18000, previous: 18000 },
  { category: "Utilities", group: "Needs", amount: 5200, previous: 4600 },
  { category: "Groceries", group: "Needs", amount: 7800, previous: 7400 },
  { category: "Transportation", group: "Needs", amount: 6800, previous: 5200 },
  { category: "Dining", group: "Wants", amount: 9200, previous: 7800 },
  { category: "Entertainment", group: "Wants", amount: 4200, previous: 3900 },
  { category: "Shopping", group: "Wants", amount: 6100, previous: 7200 },
  { category: "Travel", group: "Wants", amount: 4800, previous: 3000 },
  { category: "Mutual Funds", group: "Savings", amount: 7000, previous: 6500 },
  { category: "Emergency Fund", group: "Savings", amount: 2200, previous: 1500 }
];

export const budgetTrend = [
  { month: "Jan", needs: 28600, wants: 20100, savings: 7600 },
  { month: "Feb", needs: 30100, wants: 18800, savings: 8200 },
  { month: "Mar", needs: 31400, wants: 21600, savings: 7900 },
  { month: "Apr", needs: 32800, wants: 22800, savings: 8500 },
  { month: "May", needs: 34500, wants: 24200, savings: 9100 },
  { month: "Jun", needs: 37800, wants: 24300, savings: 9200 }
];

export const subscriptionImpact = [
  { merchant: "Netflix", amount: 649, risk: "Healthy" },
  { merchant: "Spotify", amount: 119, risk: "Healthy" },
  { merchant: "Notion", amount: 8000, risk: "Unused" },
  { merchant: "Cloud Storage", amount: 1999, risk: "Price increase" }
];
