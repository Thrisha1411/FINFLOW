"""
Hybrid AI Fraud Intelligence Engine.
Combines Isolation Forest Anomaly Detection (Liu et al.) with
Behavioral Rule Heuristics and Explainable AI Reasoning.
Designed with pure-Python resilient mathematical foundations to avoid
C-extension crashes on Windows Python 3.13 while maintaining mathematical rigor.
"""

from typing import List, Dict, Any, Optional
from decimal import Decimal
import math
import statistics
import random
from datetime import datetime, timezone


class IsolationTreeNode:
    def __init__(self, left=None, right=None, split_feature=None, split_value=None, size=1):
        self.left = left
        self.right = right
        self.split_feature = split_feature
        self.split_value = split_value
        self.size = size
        self.is_leaf = left is None and right is None


class IsolationForestEngine:
    """
    Implementation of Isolation Forest (Liu, Ting, Zhou 2008).
    Isolates anomalies by randomly selecting a feature and split value.
    Anomalies require significantly fewer partitions to isolate (shorter path lengths).
    """
    def __init__(self, n_trees: int = 50, max_samples: int = 128):
        self.n_trees = n_trees
        self.max_samples = max_samples
        self.trees: List[IsolationTreeNode] = []
        self._fit_baseline()

    def _c(self, n: int) -> float:
        """Average path length of unsuccessful search in BST."""
        if n <= 1:
            return 1.0
        if n == 2:
            return 1.0
        # Euler-Mascheroni constant = 0.5772156649
        return 2.0 * (math.log(n - 1) + 0.5772156649) - (2.0 * (n - 1) / n)

    def _build_tree(self, X: List[List[float]], current_height: int, max_height: int) -> IsolationTreeNode:
        n_samples = len(X)
        if current_height >= max_height or n_samples <= 1:
            return IsolationTreeNode(size=n_samples)

        n_features = len(X[0])
        feat_idx = random.randint(0, n_features - 1)
        feat_values = [row[feat_idx] for row in X]
        min_v, max_v = min(feat_values), max(feat_values)

        if min_v == max_v:
            return IsolationTreeNode(size=n_samples)

        split_v = random.uniform(min_v, max_v)
        left_X = [row for row in X if row[feat_idx] < split_v]
        right_X = [row for row in X if row[feat_idx] >= split_v]

        left_node = self._build_tree(left_X, current_height + 1, max_height)
        right_node = self._build_tree(right_X, current_height + 1, max_height)

        return IsolationTreeNode(
            left=left_node,
            right=right_node,
            split_feature=feat_idx,
            split_value=split_v,
            size=n_samples
        )

    def _path_length(self, x: List[float], node: IsolationTreeNode, current_height: int) -> float:
        if node.is_leaf:
            return current_height + self._c(node.size) if node.size > 1 else current_height

        feat_idx = node.split_feature
        if x[feat_idx] < node.split_value:
            return self._path_length(x, node.left, current_height + 1)
        else:
            return self._path_length(x, node.right, current_height + 1)

    def _fit_baseline(self):
        """Fits isolation trees on typical synthetic financial transaction patterns."""
        random.seed(42)
        X = []
        for _ in range(300):
            # [log_amount, hour, day, velocity]
            amt = random.expovariate(1.0 / 120.0) + 5.0
            log_amt = math.log1p(amt)
            hour = random.gauss(14.0, 3.5) % 24.0
            day = float(random.randint(0, 6))
            vel = float(min(5, max(0, int(random.gauss(1.2, 0.8)))))
            X.append([log_amt, hour, day, vel])

        max_height = math.ceil(math.log2(max(2, min(self.max_samples, len(X)))))
        self.trees = []
        for _ in range(self.n_trees):
            sample_subset = random.sample(X, min(self.max_samples, len(X)))
            tree = self._build_tree(sample_subset, 0, max_height)
            self.trees.append(tree)

    def compute_anomaly_score(self, x: List[float]) -> float:
        """
        Calculates normalized anomaly score s(x, n) = 2^(-E(h(x)) / c(n)).
        Scores close to 1.0 indicate definite anomalies.
        Scores significantly below 0.5 indicate normal instances.
        """
        if not self.trees:
            return 0.2
        path_lengths = [self._path_length(x, tree, 0) for tree in self.trees]
        avg_path = sum(path_lengths) / len(path_lengths)
        c_val = self._c(self.max_samples)
        score = 2.0 ** (- (avg_path / c_val))
        return min(1.0, max(0.0, score))


class FraudDetectionEngine:
    def __init__(self):
        self._iforest = IsolationForestEngine(n_trees=40, max_samples=64)

    def evaluate_transaction(
        self,
        amount: Decimal,
        merchant_name: str,
        historical_txs: List[Dict[str, Any]],
        current_time: datetime = None,
        device_is_new: bool = False,
        failed_attempts_count: int = 0
    ) -> Dict[str, Any]:
        """
        Executes hybrid fraud evaluation.
        Returns risk_score (0-100), risk_level, recommendation, triggered_rules, and evidence.
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)
        if current_time.tzinfo is not None:
            current_time = current_time.replace(tzinfo=None)

        amt_float = float(abs(amount))
        triggered_rules = []
        evidence_list = []
        rule_score_total = 0.0

        # --- RULE 1: Historical Mean & Standard Deviation Anomaly ---
        if historical_txs:
            amounts = [float(abs(tx["amount"])) for tx in historical_txs]
            mean_amt = statistics.mean(amounts)
            std_amt = statistics.stdev(amounts) if len(amounts) > 1 else max(10.0, mean_amt * 0.5)
            if std_amt < 1.0:
                std_amt = 10.0

            z_score = (amt_float - mean_amt) / std_amt
            if z_score > 3.0:
                pts = min(40.0, 15.0 + (z_score - 3.0) * 8.0)
                rule_score_total += pts
                triggered_rules.append({
                    "rule_code": "RUL-AMT-SPIKE",
                    "signal_name": "Significant Statistical Outlier",
                    "severity": "CRITICAL" if z_score > 4.5 else "HIGH",
                    "weight": 0.85,
                    "description": f"Transaction amount (${amt_float:,.2f}) is {z_score:.1f} standard deviations above historical 30-day average (${mean_amt:,.2f})."
                })
                evidence_list.append(f"Amount exceeds 30-day historical mean (${mean_amt:.2f}) by {((amt_float / max(1.0, mean_amt)) - 1.0)*100:.0f}%.")
        else:
            if amt_float > 5000:
                rule_score_total += 25.0
                triggered_rules.append({
                    "rule_code": "RUL-AMT-COLD-HIGH",
                    "signal_name": "High Value Initial Transaction",
                    "severity": "MEDIUM",
                    "weight": 0.6,
                    "description": f"Initial transaction for account is unusually large (${amt_float:,.2f})."
                })

        # --- RULE 2: Velocity & Rapid Frequency Bursts (5-minute window) ---
        rapid_burst_txs = []
        for tx in historical_txs:
            t_dt = tx.get("created_at", current_time)
            if t_dt and t_dt.tzinfo is not None:
                t_dt = t_dt.replace(tzinfo=None)
            if 0 <= (current_time - t_dt).total_seconds() < 300:
                rapid_burst_txs.append(tx)
        burst_count = len(rapid_burst_txs) + 1
        if burst_count >= 8:
            rule_score_total += 35.0
            triggered_rules.append({
                "rule_code": "RUL-VEL-BURST",
                "signal_name": "Rapid Velocity Burst",
                "severity": "CRITICAL",
                "weight": 0.90,
                "description": f"Detected {burst_count} rapid transactions initiated within 5 minutes."
            })
            evidence_list.append(f"High velocity burst: {burst_count} transactions within 5 minutes.")
        elif burst_count >= 5:
            rule_score_total += 15.0
            triggered_rules.append({
                "rule_code": "RUL-VEL-ELEVATED",
                "signal_name": "Elevated Transaction Frequency",
                "severity": "MEDIUM",
                "weight": 0.50,
                "description": f"Detected {burst_count} transactions initiated within 5 minutes."
            })

        # --- RULE 3: Device Trust & Fingerprint Change ---
        if device_is_new:
            rule_score_total += 20.0
            triggered_rules.append({
                "rule_code": "RUL-DEV-UNRECOGNIZED",
                "signal_name": "Unrecognized Device Fingerprint",
                "severity": "MEDIUM",
                "weight": 0.65,
                "description": "Transaction initiated from a device never previously authenticated by this account."
            })
            evidence_list.append("New/unrecognized device detected.")

        # --- RULE 4: Failed Attempt Surge ---
        if failed_attempts_count >= 3:
            rule_score_total += 30.0
            triggered_rules.append({
                "rule_code": "RUL-AUTH-FAILED-SURGE",
                "signal_name": "Multiple Prior Failed Payment Attempts",
                "severity": "CRITICAL",
                "weight": 0.95,
                "description": f"{failed_attempts_count} consecutive payment failures immediately preceded this transaction."
            })
            evidence_list.append(f"{failed_attempts_count} consecutive payment failures preceded this attempt.")

        # --- RULE 5: High Risk Merchant Keywords ---
        merchant_lower = merchant_name.lower()
        suspicious_keywords = ["unknown", "crypto", "casino", "wire offshore", "anonymous", "shell corp"]
        if any(kw in merchant_lower for kw in suspicious_keywords):
            rule_score_total += 35.0
            triggered_rules.append({
                "rule_code": "RUL-MERCHANT-HIGH-RISK",
                "signal_name": "High-Risk Merchant Descriptor",
                "severity": "HIGH",
                "weight": 0.80,
                "description": f"Merchant descriptor '{merchant_name}' matches monitored risk patterns."
            })
            evidence_list.append(f"Merchant '{merchant_name}' flagged by risk registry.")

        # --- ISOLATION FOREST ANOMALY SCORE ---
        hour = float(current_time.hour)
        day = float(current_time.weekday())
        log_amt = math.log1p(amt_float)
        feature_vec = [log_amt, hour, day, float(burst_count)]
        
        raw_if_score = self._iforest.compute_anomaly_score(feature_vec)
        # Scale 0.4-0.8 to 0-100%
        ml_risk_pct = min(100.0, max(0.0, (raw_if_score - 0.35) * 220.0))

        # --- HYBRID ENSEMBLE COMBINATION ---
        final_risk_score = min(100.0, (rule_score_total * 0.65) + (ml_risk_pct * 0.35))
        final_risk_score = round(final_risk_score, 1)

        # Classification & Action
        if final_risk_score >= 85.0:
            risk_level = "CRITICAL"
            recommendation = "BLOCK"
        elif final_risk_score >= 65.0:
            risk_level = "HIGH"
            recommendation = "STEP_UP_AUTH"
        elif final_risk_score >= 35.0:
            risk_level = "MEDIUM"
            recommendation = "MANUAL_REVIEW"
        else:
            risk_level = "LOW"
            recommendation = "APPROVE"

        return {
            "risk_score": final_risk_score,
            "risk_level": risk_level,
            "recommendation": recommendation,
            "ml_anomaly_score": round(ml_risk_pct, 1),
            "triggered_rules": triggered_rules,
            "supporting_evidence": evidence_list,
            "model_version": "FinFlow-Hybrid-IF-1.2.0",
            "evaluated_at": current_time.isoformat()
        }

fraud_engine = FraudDetectionEngine()
