import { budgetProfiles, budgetSpending, demoFraudDecision, demoTransactions, subscriptionImpact } from "../api/demoData";
import { formatInr } from "./format";

export type Intent =
  | "Budget Analysis"
  | "Transaction Investigation"
  | "Fraud Investigation"
  | "Forecasting"
  | "Subscription Analysis"
  | "Savings Optimization";

export type InsightResponse = {
  intent: Intent;
  answer: string;
  reasoning: string;
  confidence: number;
  evidence: string[];
  action: string;
  memory: string;
};

export function classifyIntent(question: string): Intent {
  const q = question.toLowerCase();
  if (q.includes("fraud") || q.includes("flagged") || q.includes("risk")) return "Fraud Investigation";
  if (q.includes("transaction") || q.includes("payment") || q.includes("failed")) return "Transaction Investigation";
  if (q.includes("forecast") || q.includes("predict") || q.includes("next month")) return "Forecasting";
  if (q.includes("subscription") || q.includes("renewal") || q.includes("cancel")) return "Subscription Analysis";
  if (q.includes("save") || q.includes("saving") || q.includes("emergency")) return "Savings Optimization";
  return "Budget Analysis";
}

export function retrieveContext(intent: Intent) {
  const needs = budgetSpending.filter((item) => item.group === "Needs");
  const wants = budgetSpending.filter((item) => item.group === "Wants");
  const savings = budgetSpending.filter((item) => item.group === "Savings");
  return {
    transactions: demoTransactions,
    budgets: budgetSpending,
    forecasts: { diningGrowth: 15, nextMonthSpend: 6120000, annualSavingsRisk: 42000 },
    subscriptions: subscriptionImpact,
    fraudReports: [demoFraudDecision],
    auditLogs: ["approval.updated", "login.suspicious", "fraud.case.created"],
    allocation: {
      needs: needs.reduce((sum, item) => sum + item.amount, 0),
      wants: wants.reduce((sum, item) => sum + item.amount, 0),
      savings: savings.reduce((sum, item) => sum + item.amount, 0)
    },
    intent
  };
}

export function buildFinancialInsight(question: string, previousMemory = ""): InsightResponse {
  const intent = classifyIntent(question);
  const context = retrieveContext(intent);
  const largeTransaction = context.transactions.find((item) => item.risk_score > 75);
  const unusedSubscription = context.subscriptions.find((item) => item.risk === "Unused");
  const target = budgetProfiles["Working Professional"];
  const income = 60000;
  const currentNeeds = Math.round((context.allocation.needs / income) * 100);
  const currentWants = Math.round((context.allocation.wants / income) * 100);
  const currentSavings = Math.round((context.allocation.savings / income) * 100);

  if (intent === "Fraud Investigation" || (question.toLowerCase().includes("what should i do") && previousMemory.includes("Fraud"))) {
    return {
      intent: "Fraud Investigation",
      answer: `${largeTransaction?.merchant ?? "The high-risk payment"} was flagged because the amount, velocity, and payment pattern are outside the normal range.`,
      reasoning: demoFraudDecision.fraud_reason,
      confidence: 91,
      evidence: [`Risk score ${demoFraudDecision.risk_score}`, `${largeTransaction?.merchant}: ${formatInr(largeTransaction?.amount)}`, "Recent audit event: fraud.case.created"],
      action: "Hold the payment, verify the device, and require finance manager approval.",
      memory: "Fraud Investigation: high-risk INR transfer"
    };
  }

  if (intent === "Forecasting") {
    return {
      intent,
      answer: `Next month spend is likely to trend higher, with dining expected to rise 15% and controllable subscriptions adding ${formatInr(10767)}.`,
      reasoning: "Forecast combines category trend, recurring renewals, and the previous budget performance pattern.",
      confidence: 84,
      evidence: ["Dining +15% predicted", "Travel +8% predicted", `Forecast spend ${formatInr(context.forecasts.nextMonthSpend)}`],
      action: "Set stricter dining and travel limits before the next billing cycle.",
      memory: "Forecasting: dining and subscriptions are the main next-month risks"
    };
  }

  if (intent === "Subscription Analysis") {
    return {
      intent,
      answer: `${unusedSubscription?.merchant ?? "One subscription"} appears unused and can be reviewed for cancellation.`,
      reasoning: "Subscription impact is high relative to discretionary budget and one renewal is marked unused.",
      confidence: 88,
      evidence: context.subscriptions.map((item) => `${item.merchant}: ${formatInr(item.amount)} (${item.risk})`),
      action: "Cancel Notion or downgrade before renewal, then reallocate that amount to emergency savings.",
      memory: "Subscription Analysis: Notion is unused"
    };
  }

  if (intent === "Savings Optimization") {
    return {
      intent,
      answer: `You can save about ${formatInr(3500)} per month by reducing food delivery and cancelling unused subscriptions.`,
      reasoning: "Savings rate is below the profile target and wants have several flexible categories.",
      confidence: 86,
      evidence: [`Current savings ${currentSavings}% vs target ${target.Savings}%`, "Dining increased 18%", "Notion unused"],
      action: "Automate an extra savings transfer after salary credit and cap dining spend weekly.",
      memory: "Savings Optimization: recover savings through dining and subscription cuts"
    };
  }

  if (intent === "Transaction Investigation") {
    return {
      intent,
      answer: "The transaction list shows one high-risk IMPS payment and one approval-pending vendor payment.",
      reasoning: "Risk scores are derived from amount, transaction status, and velocity patterns.",
      confidence: 82,
      evidence: context.transactions.map((item) => `${item.merchant}: ${item.status}, risk ${item.risk_score}`),
      action: "Review flagged items first, then retry only low-risk processing failures.",
      memory: "Transaction Investigation: review flagged IMPS first"
    };
  }

  return {
    intent,
    answer: `Your current allocation is Needs ${currentNeeds}%, Wants ${currentWants}%, Savings ${currentSavings}% against a ${target.Needs}/${target.Wants}/${target.Savings} working-professional plan.`,
    reasoning: "Needs exceed the recommended allocation, mainly because transportation and utilities are elevated.",
    confidence: 89,
    evidence: [`Needs ${formatInr(context.allocation.needs)}`, `Wants ${formatInr(context.allocation.wants)}`, `Savings ${formatInr(context.allocation.savings)}`],
    action: "Reduce transportation and utility costs first, then increase the emergency fund contribution.",
    memory: "Budget Analysis: needs are above target"
  };
}
