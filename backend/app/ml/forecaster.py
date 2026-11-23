"""
Predictive Spending & Cash Flow Forecasting Engine.
Uses Holt's Linear Exponential Smoothing with pure-Python statistics,
calculating next-month spending forecasts, confidence intervals, and overspending probability.
"""

from typing import List, Dict, Any
from decimal import Decimal
import math
import statistics
from datetime import datetime, timezone

class SpendingForecaster:
    @staticmethod
    def forecast_spending(
        monthly_expenses: List[Dict[str, Any]],
        recurring_commitments: Decimal = Decimal("0.00"),
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Calculates next-month forecast, confidence intervals, and overspending probability.
        monthly_expenses: list of dicts [{'month': '2026-08', 'total': 18500.0, 'categories': {...}}]
        """
        if not monthly_expenses or len(monthly_expenses) < 2:
            baseline = float(recurring_commitments) * 1.35 if recurring_commitments > 0 else 15000.0
            return {
                "forecast_amount": round(baseline, 2),
                "lower_bound": round(baseline * 0.85, 2),
                "upper_bound": round(baseline * 1.20, 2),
                "confidence_level": confidence_level,
                "overspending_probability": 0.25,
                "trend_direction": "STABLE",
                "trend_percentage": 0.0,
                "recurring_commitments": float(recurring_commitments),
                "method": "BASELINE_HEURISTIC",
                "notes": "Insufficient historical months (<2) for seasonal smoothing. Baseline generated."
            }

        totals = [float(m["total"]) for m in monthly_expenses]
        n = len(totals)
        
        # Exponential Smoothing (Holt's Linear Trend)
        alpha = 0.4
        beta = 0.2
        
        level = totals[0]
        trend = totals[1] - totals[0] if n > 1 else 0.0
        
        for i in range(1, n):
            prev_level = level
            level = alpha * totals[i] + (1 - alpha) * (level + trend)
            trend = beta * (level - prev_level) + (1 - beta) * trend

        raw_forecast = level + trend
        commitments_float = float(recurring_commitments)
        forecast_amount = max(raw_forecast, commitments_float * 1.05)

        # Standard error and confidence intervals
        residuals = [totals[i] - (totals[i-1] + trend) for i in range(1, n)]
        std_err = statistics.stdev(residuals) if len(residuals) > 1 else (statistics.mean(totals) * 0.1)
        z_multiplier = 1.96 if confidence_level == 0.95 else 1.645
        
        margin = z_multiplier * std_err
        lower_bound = max(commitments_float, forecast_amount - margin)
        upper_bound = forecast_amount + margin

        # Overspending probability
        last_month_total = totals[-1]
        diff_pct = ((forecast_amount - last_month_total) / max(1.0, last_month_total)) * 100.0
        
        if diff_pct > 15.0:
            trend_direction = "INCREASING"
            overspending_prob = min(0.95, 0.50 + (diff_pct / 100.0))
        elif diff_pct < -5.0:
            trend_direction = "DECREASING"
            overspending_prob = max(0.05, 0.30 - (abs(diff_pct) / 100.0))
        else:
            trend_direction = "STABLE"
            overspending_prob = 0.28

        return {
            "forecast_amount": round(forecast_amount, 2),
            "lower_bound": round(lower_bound, 2),
            "upper_bound": round(upper_bound, 2),
            "confidence_level": confidence_level,
            "overspending_probability": round(overspending_prob, 2),
            "trend_direction": trend_direction,
            "trend_percentage": round(diff_pct, 1),
            "recurring_commitments": commitments_float,
            "method": "EXPONENTIAL_SMOOTHING_HOLT",
            "historical_sample_size": n
        }

forecaster = SpendingForecaster()
