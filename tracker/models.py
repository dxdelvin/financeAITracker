from django.db import models
from django.utils import timezone
# Create your models here.


class Transaction(models.Model):
    CATEGORY_CHOICES = [
        ('Housing & Utilities', '🏠 Housing & Utilities'),
        ('Food & Groceries', '🛒 Food & Groceries'),
        ('Transportation', '🚗 Transportation'),
        ('Health & Wellness', '🏥 Health & Wellness'),
        ('Entertainment & Leisure', '🎬 Entertainment & Leisure'),
        ('Education & Learning', '📚 Education & Learning'),
        ('Gifts & Donations', '🎁 Gifts & Donations'),
        ('Insurance & Taxes', '🏦 Insurance & Taxes'),
        ('Business & Work', '💼 Business & Work'),
        ('Travel & Vacations', '✈️ Travel & Vacations'),
        ('Pets & Animals', '🐾 Pets & Animals'),
        ('Subscriptions & Memberships', '📅 Subscriptions & Memberships'),
        ('Miscellaneous', '🔄 Miscellaneous/Others'),
    ]

    TRANSACTION_TYPE_CHOICES = [
        ('Expense', 'Expense'),
        ('Income', 'Income'),
    ]

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPE_CHOICES)
    comment = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.category} - {self.amount} ({self.transaction_type})"
