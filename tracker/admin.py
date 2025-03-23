from django.contrib import admin
from .models import Transaction
# Register your models here.

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('amount', 'category', 'transaction_type', 'date_created')
    ordering = ['-date_created']