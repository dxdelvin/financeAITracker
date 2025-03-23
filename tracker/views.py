from django.shortcuts import render, redirect, get_object_or_404
from .models import Transaction
from .forms import TransactionForm
from django.utils import timezone
from django.utils.timezone import now

def home(request):
    # Handle form submission for adding a new transaction
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            if not transaction.date_created:  # If no date is provided, use the current date
                transaction.date_created = timezone.now()
            transaction.save()
            return redirect('home')  # Redirect to the home page after saving
    else:
        form = TransactionForm()

    today = now().date()
    current_month = today.month
    current_year = today.year

    transactions = Transaction.objects.all().order_by('-date_created')
    monthly_transactions = transactions.filter(date_created__year=current_year, date_created__month=current_month)

    total_income = sum(t.amount for t in transactions if t.transaction_type == "Income")
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == "Expense")
    balance = total_income - total_expenses

    total_income = sum(t.amount for t in monthly_transactions if t.transaction_type == "Income")
    total_expenses = sum(t.amount for t in monthly_transactions if t.transaction_type == "Expense")
    print(Transaction.objects.filter(date_created__year=current_year, date_created__month=current_month))

    return render(request, 'home.html', {
        'form': form,
        'transactions': transactions,  # Show all transactions
        'total_income': total_income,  # This month's income
        'total_expenses': total_expenses,  # This month's expenses
        'balance':balance
    })

def delete_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    transaction.delete()
    return redirect('home')
