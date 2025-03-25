import re
import json
import dateparser
from datetime import date, datetime, timedelta
from django.conf import settings
import requests
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import heapq

nltk.download('punkt')
nltk.download('stopwords')

class TransactionParser:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
        self.headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}

        # Category mapping with clear priorities
        self.category_keywords = {
            'Subscriptions & Memberships': [
                'netflix', 'spotify', 'prime', 'subscription', 'membership', 'streaming',
                'hulu', 'disney+', 'apple music', 'youtube premium', 'patreon', 'magazine',
                'newspaper', 'gym membership', 'cloud storage', 'vpn', 'adobe', 'dropbox'
            ],
            'Business & Work': [
                'salary', 'paycheck', 'freelance', 'client', 'invoice', 'commission',
                'bonus', 'stipend', 'consulting', 'contractor', 'business expense',
                'coworking', 'reimbursement', 'remote work', 'office supplies', 'workshop'
            ],
            'Housing & Utilities': [
                'rent', 'mortgage', 'electric', 'water', 'gas', 'internet', 'wifi',
                'phone bill', 'utility', 'heating', 'cooling', 'landlord', 'lease',
                'property tax', 'maintenance', 'home security', 'plumbing', 'repair'
            ],
            'Food & Groceries': [
                'grocery', 'supermarket', 'food', 'restaurant', 'coffee', 'dining',
                'snack', 'fast food', 'takeout', 'delivery', 'ubereats', 'doordash',
                'meal', 'bakery', 'bar', 'wine', 'alcohol', 'beverage', 'farmers market'
            ],
            'Transportation': [
                'fuel', 'gas', 'metro', 'bus', 'train', 'car', 'uber', 'lyft', 'taxi',
                'toll', 'parking', 'public transport', 'bike', 'subway', 'car rental',
                'aviation', 'road trip', 'flight ticket', 'rideshare'
            ],
            'Health & Wellness': [
                'hospital', 'doctor', 'medicine', 'pharmacy', 'gym', 'yoga', 'dentist',
                'optometrist', 'therapy', 'mental health', 'insurance', 'supplement',
                'protein', 'workout', 'spa', 'massage', 'personal trainer', 'wellness'
            ],
            'Entertainment & Leisure': [
                'movie', 'concert', 'hobby', 'game', 'golf', 'bowling', 'theme park',
                'amusement', 'music festival', 'club', 'nightlife', 'board game',
                'casino', 'theater', 'arcade', 'sports event', 'ticket'
            ],
            'Travel & Vacations': [
                'flight', 'hotel', 'vacation', 'airbnb', 'resort', 'cruise', 'travel',
                'rental car', 'tour', 'passport', 'visa', 'backpacking', 'road trip',
                'sightseeing', 'beach', 'skiing', 'camping', 'luggage'
            ],
            'Education & Learning': [
                'book', 'course', 'school', 'tuition', 'seminar', 'college', 'university',
                'training', 'certification', 'exam', 'tutor', 'education', 'textbook',
                'study material', 'library', 'scholarship', 'online course'
            ],
            'Gifts & Donations': [
                'gift', 'donation', 'charity', 'tip', 'wedding', 'birthday', 'anniversary',
                'fundraiser', 'crowdfunding', 'go fund me', 'church donation', 'nonprofit',
                'volunteering', 'christmas gift', 'present'
            ],
            'Pets & Animals': [
                'pet', 'vet', 'dog', 'cat', 'food', 'toys', 'adoption', 'grooming',
                'boarding', 'kennel', 'pet hospital', 'leash', 'collar', 'treats',
                'aquarium', 'bird food', 'hamster', 'fish tank', 'litter box'
            ],
            'Insurance & Taxes': [
                'insurance', 'tax', 'premium', 'deductible', 'policy', 'auto insurance',
                'health insurance', 'home insurance', 'life insurance', 'car insurance',
                'claim', 'tax return', 'property tax', 'income tax', 'social security'
            ],
            'Miscellaneous': [
                'other', 'misc', 'fee', 'bank', 'transfer', 'atm', 'service charge',
                'paypal', 'cashapp', 'venmo', 'wire transfer', 'late fee', 'overdraft',
                'penalty', 'subscription fee', 'unknown expense'
            ]
        }

    def parse_transaction(self, text):
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
        amount_match = re.search(r'\$?\s*(\d+[\.,]?\d*)', text)
        if amount_match:
            try:
                return round(float(amount_match.group(1).replace(',', '')), 2)
            except:
                return None
        return None


    def _extract_date(self, text):
        date_pattern = r'\b(\d{1,2}[st|nd|rd|th]*\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\b|\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2})\b'
        matches = re.findall(date_pattern, text, re.IGNORECASE)

        if matches:
            parsed_date = dateparser.parse(matches[0], settings={'PREFER_DATES_FROM': 'past'})
            if parsed_date:
                return parsed_date.date()

        today = datetime.today()

        relative_dates = {
            "yesterday": today - timedelta(days=1),
            "day before yesterday": today - timedelta(days=2),
            "tomorrow": today + timedelta(days=1),
            "next week": today + timedelta(weeks=1),
            "last week": today - timedelta(weeks=1),
            "next month": today.replace(month=today.month + 1) if today.month < 12 else today.replace(year=today.year + 1, month=1),
            "last month": today.replace(month=today.month - 1) if today.month > 1 else today.replace(year=today.year - 1, month=12),
            "this week": today - timedelta(days=today.weekday()),  # Start of current week (Monday)
            "next year": today.replace(year=today.year + 1),
            "last year": today.replace(year=today.year - 1),
            "in a week": today + timedelta(weeks=1),
            "in two weeks": today + timedelta(weeks=2),
            "in a month": today + timedelta(weeks=4),  # Approx. 4 weeks
            "last weekend": today - timedelta(days=(today.weekday() + 2) % 7),  # Previous Saturday
            "next weekend": today + timedelta(days=(5 - today.weekday()) % 7),  # Next Saturday
        }

        for phrase, date in relative_dates.items():
            if phrase in text.lower():
                return date.date()

        return today.date()


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
        if not text or amount is None:
            return "Invalid transaction"

        stop_words = set(stopwords.words("english"))
        words = word_tokenize(text.lower())

        word_frequencies = {}
        for word in words:
            if word not in stop_words and word.isalnum():
                word_frequencies[word] = word_frequencies.get(word, 0) + 1

        max_freq = max(word_frequencies.values()) if word_frequencies else 1
        for word in word_frequencies:
            word_frequencies[word] /= max_freq

        sentence_scores = {}
        sentences = sent_tokenize(text)

        for sentence in sentences:
            for word in word_tokenize(sentence.lower()):
                if word in word_frequencies:
                    sentence_scores[sentence] = sentence_scores.get(sentence, 0) + word_frequencies[word]

        summary_sentences = heapq.nlargest(3, sentence_scores, key=sentence_scores.get)
        summary = " ".join(summary_sentences)

        return summary[:200] + "..." if len(summary) > 200 else summary

    def parse_with_ai(self, text):
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