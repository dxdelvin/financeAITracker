import re
import json
import dateparser
from datetime import date
from django.conf import settings
import requests


class TransactionParser:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
        self.headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}

        # Category mapping with clear priorities
        self.category_keywords = {
            'Subscriptions & Memberships': [
                'netflix', 'spotify', 'prime', 'subscription', 'membership', 'streaming'
            ],
            'Business & Work': ['salary', 'paycheck', 'freelance', 'client', 'invoice'],
            'Housing & Utilities': ['rent', 'mortgage', 'electric', 'water', 'gas', 'internet'],
            'Food & Groceries': ['grocery', 'supermarket', 'food', 'restaurant', 'coffee', 'dining'],
            'Transportation': ['fuel', 'gas', 'metro', 'bus', 'train', 'car', 'uber', 'lyft'],
            'Health & Wellness': ['hospital', 'doctor', 'medicine', 'pharmacy', 'gym', 'yoga'],
            'Entertainment & Leisure': ['movie', 'concert', 'hobby', 'game', 'golf', 'bowling'],
            'Travel & Vacations': ['flight', 'hotel', 'vacation', 'airbnb', 'resort'],
            'Education & Learning': ['book', 'course', 'school', 'tuition', 'seminar'],
            'Gifts & Donations': ['gift', 'donation', 'charity', 'tip', 'wedding'],
            'Pets & Animals': ['pet', 'vet', 'dog', 'cat', 'food', 'toys'],
            'Insurance & Taxes': ['insurance', 'tax', 'premium', 'deductible'],
            'Miscellaneous': ['other', 'misc', 'fee', 'bank', 'transfer']
        }

    def parse_transaction(self, text):
        """Main method to parse a transaction"""
        # Step 1: Extract amount
        amount = self._extract_amount(text)

        # Step 2: Extract date (fallback to today if missing)
        trans_date = self._extract_date(text)

        # Step 3: Determine category
        category = self._determine_category(text)

        # Step 4: Determine transaction type
        trans_type = self._determine_transaction_type(text)

        # Step 5: Generate summary
        summary = self._generate_summary(text, category, amount)

        # Step 6: Validate and return result
        return {
            'summary': summary,
            'amount': amount,
            'date': trans_date.isoformat(),
            'category': category,
            'type': trans_type,
            'valid': amount is not None
        }

    def _extract_amount(self, text):
        """Extract amount from text"""
        amount_match = re.search(r'\$?\s*(\d+[\.,]?\d*)', text)
        if amount_match:
            try:
                return round(float(amount_match.group(1).replace(',', '')), 2)
            except:
                return None
        return None

    def _extract_date(self, text):
        """Extract date from text (fallback to today)"""
        parsed_date = dateparser.parse(text, settings={'PREFER_DATES_FROM': 'past'})
        return parsed_date.date() if parsed_date else date.today()

    def _determine_category(self, text):
        """Determine category based on keywords"""
        text_lower = text.lower()
        for category, keywords in self.category_keywords.items():
            if any(f' {kw} ' in f' {text_lower} ' for kw in keywords):
                return category
        return 'Miscellaneous'

    def _determine_transaction_type(self, text):
        """Determine if transaction is Income or Expense"""
        text_lower = text.lower()
        income_keywords = ['salary', 'income', 'received', 'payment', 'refund']
        return 'Income' if any(kw in text_lower for kw in income_keywords) else 'Expense'

    def _generate_summary(self, text, category, amount):
        """Generate a clean summary"""
        if amount is None:
            return "Invalid transaction"

        # Basic summary format: "Category: $X.XX"
        return f"{category}: ${amount:.2f}"

    def parse_with_ai(self, text):
        """Optional AI parsing for advanced cases"""
        prompt = f"""Analyze this transaction:
        {text}

        Return JSON with:
        - amount (float)
        - category (string)
        - date (YYYY-MM-DD)
        - type (Income/Expense)
        - valid (true/false)"""

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"inputs": prompt, "parameters": {"max_new_tokens": 200}}
            )

            if response.status_code == 200:
                result = response.json()[0]['generated_text']
                json_str = re.search(r'\{.*\}', result, re.DOTALL).group()
                json_str = json_str.replace("'", '"').replace("True", "true").replace("False", "false")
                return json.loads(json_str)
        except:
            return None