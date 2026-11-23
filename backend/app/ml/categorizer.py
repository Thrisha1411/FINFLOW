"""
Intelligent Auto-Categorization Engine.
Classifies transactions into 15 standard financial categories using
merchant pattern matching, text descriptors, and user feedback learning.
"""

from typing import Dict, Any, List, Optional
import re

CATEGORY_TAXONOMY = {
    "Food and Dining": ["restaurant", "cafe", "coffee", "starbucks", "mcdonalds", "chipotle", "whole foods", "grocery", "trader joe", "cater", "uber eats", "doordash", "grubhub", "diner", "bakery", "subway"],
    "Shopping": ["amazon", "apple store", "walmart", "target", "best buy", "clothing", "zara", "nike", "ebay", "ikea", "nordstrom", "retail"],
    "Transportation": ["uber", "lyft", "chevron", "shell", "gas", "fuel", "subway", "transit", "metro", "parking", "train", "toll", "airline", "delta", "united"],
    "Healthcare": ["pharmacy", "cvs", "walgreens", "hospital", "clinic", "dental", "doctor", "bluecross", "optometry", "medical", "health"],
    "Utilities": ["electric", "water", "gas co", "power", "energy", "internet", "comcast", "at&t", "verizon", "t-mobile", "broadband"],
    "Rent": ["wework", "property", "lease", "rent", "realty", "apartments", "housing", "landlord"],
    "Entertainment": ["netflix", "spotify", "hulu", "disney", "amc", "theatre", "steam", "playstation", "cinema", "concert", "ticketmaster"],
    "Travel": ["hotel", "airbnb", "marriott", "hilton", "expedia", "booking.com", "flight", "car rental", "delta airlines", "american airlines"],
    "Education": ["coursera", "udemy", "university", "college", "tuition", "school", "books", "edx", "academy"],
    "Salary": ["payroll", "salary", "stripe settlement", "direct deposit", "wages", "employer"],
    "Investments": ["vanguard", "fidelity", "robinhood", "charles schwab", "brokerage", "etrade", "dividend", "yield"],
    "Savings": ["savings transfer", "deposit", "reserve", "emergency fund", "auto-save"],
    "Insurance": ["geico", "progressive", "allstate", "state farm", "metlife", "prudential", "liability policy", "insurance"],
    "Business Expenses": ["aws", "cloud", "slack", "github", "google workspace", "zoom", "jira", "atlassian", "salesforce", "microsoft", "notion", "figma", "bloomberg"],
    "Other": []
}

class TransactionCategorizer:
    def __init__(self):
        self._custom_corrections: Dict[str, str] = {}

    def register_correction(self, merchant_name: str, category_name: str):
        """User feedback loop: memorizes user corrections for future classification."""
        cleaned = merchant_name.strip().lower()
        self._custom_corrections[cleaned] = category_name

    def classify(self, merchant_name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Classifies merchant name & description into a category with confidence score and explanation.
        """
        raw_text = f"{merchant_name} {description or ''}".lower()
        cleaned_merchant = merchant_name.strip().lower()

        # 1. Exact or prefix match from user correction feedback loop
        if cleaned_merchant in self._custom_corrections:
            cat = self._custom_corrections[cleaned_merchant]
            return {
                "category": cat,
                "confidence": 0.99,
                "explanation": f"Categorized via user correction preference for '{merchant_name}'.",
                "alternatives": ["Business Expenses", "Shopping"],
                "source": "USER_FEEDBACK"
            }

        for corrected_m, cat in self._custom_corrections.items():
            if corrected_m in cleaned_merchant:
                return {
                    "category": cat,
                    "confidence": 0.95,
                    "explanation": f"Matches user previous rule for '{corrected_m}'.",
                    "alternatives": ["Business Expenses", "Other"],
                    "source": "USER_FEEDBACK"
                }

        # 2. Pattern matching against taxonomy keywords
        scores: Dict[str, int] = {}
        matched_keywords: Dict[str, List[str]] = {}

        for cat, keywords in CATEGORY_TAXONOMY.items():
            scores[cat] = 0
            matched_keywords[cat] = []
            for kw in keywords:
                pattern = r'\b' + re.escape(kw) + r'\b'
                if re.search(pattern, raw_text):
                    scores[cat] += 2
                    matched_keywords[cat].append(kw)
                elif kw in raw_text:
                    scores[cat] += 1
                    matched_keywords[cat].append(kw)

        best_category = "Other"
        best_score = 0
        alternatives = []

        # Sort categories by score descending
        sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        if sorted_cats and sorted_cats[0][1] > 0:
            best_category = sorted_cats[0][0]
            best_score = sorted_cats[0][1]
            alternatives = [c for c, s in sorted_cats[1:4] if s > 0]
            if not alternatives:
                alternatives = ["Other", "Business Expenses"]

        # Calculate confidence
        if best_score >= 3:
            confidence = 0.92
            explanation = f"High confidence match on keywords: {', '.join(matched_keywords[best_category])}."
        elif best_score >= 1:
            confidence = 0.78
            explanation = f"Matched keyword indicator: '{matched_keywords[best_category][0]}'."
        else:
            confidence = 0.40
            best_category = "Other"
            explanation = "No standard merchant keywords identified. Defaulted to Other."
            alternatives = ["Business Expenses", "Shopping", "Food and Dining"]

        return {
            "category": best_category,
            "confidence": confidence,
            "explanation": explanation,
            "alternatives": alternatives[:3],
            "source": "PATTERN_NLP_ENGINE"
        }

categorizer = TransactionCategorizer()
