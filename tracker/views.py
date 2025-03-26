from django.shortcuts import render, redirect, get_object_or_404
from .models import Transaction
from .forms import TransactionForm
from django.utils import timezone
from django.contrib import messages
from .ai_processor import TransactionParser
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import date, timedelta, datetime
import json

def home(request):
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year

    # Get all transactions
    transactions = Transaction.objects.all().order_by('-date_created')
    monthly_transactions = transactions.filter(
        date_created__year=current_year,
        date_created__month=current_month
    )

    # Calculate totals
    total_income = sum(t.amount for t in monthly_transactions if t.transaction_type == "Income")
    total_expenses = sum(t.amount for t in monthly_transactions if t.transaction_type == "Expense")
    balance = total_income - total_expenses

    initial_data = request.session.pop('ai_transaction_data', None)
    form = TransactionForm(initial=initial_data) if initial_data else TransactionForm()

    if request.method == 'POST':
        if 'add_transaction' in request.POST:
            form = TransactionForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Transaction added successfully")

                if 'ai_transaction_data' in request.session:
                    del request.session['ai_transaction_data']

                return redirect('home')
            else:
                messages.error(request, "There was an error with the form. Please try again.")

        elif 'ai_describe_transaction' in request.POST:
            description = request.POST.get('ai_description', '').strip()
            if not description:
                messages.error(request, "Please describe your transaction")
                return redirect('home')

            parser = TransactionParser()
            analysis_result = parser.parse_transaction(description)

            if not analysis_result or not analysis_result.get('valid'):
                messages.error(request, "Couldn't process. Example: 'Bought groceries for $50'")
                return redirect('home')

            # Store in session instead of saving
            request.session['ai_transaction_data'] = {
                'amount': analysis_result['amount'],
                'category': analysis_result['category'],
                'transaction_type': analysis_result['type'],
                'comment': analysis_result.get('summary', ''),
                'date_created': analysis_result.get('date', timezone.now().date())
            }
            return redirect('home')

    # Render the template for GET requests
    context = {
        'form': form,
        'transactions': transactions,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
    }
    return render(request, 'home.html', context)

def delete_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    transaction.delete()
    messages.success(request, "Transaction deleted!")
    return redirect('home')



def reports(request):
    days = request.GET.get('days')
    start_date = None
    end_date = date.today()

    # Handle custom date range
    if request.GET.get('startDate') and request.GET.get('endDate'):
        try:
            start_date = datetime.strptime(request.GET.get('startDate'), "%Y-%m-%d").date()
            end_date = datetime.strptime(request.GET.get('endDate'), "%Y-%m-%d").date()
        except ValueError:
            start_date = date.today() - timedelta(days=7)
    elif days:
        if days == "thismonth":
            start_date = end_date.replace(day=1)
        elif days == "thisyear":
            start_date = end_date.replace(month=1, day=1)  # Start of current year
        elif days == "lastyear":
            start_date = date(end_date.year - 1, 1, 1)  # Start of previous year
            end_date = date(end_date.year - 1, 12, 31)  # End of previous year
        elif days == "7":
            start_date = end_date - timedelta(days=7)
        elif days == "30":
            start_date = end_date - timedelta(days=30)
        elif days == "365":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=7)
    else:
        start_date = end_date - timedelta(days=7)

    # Filter transactions based on date range
    transactions = Transaction.objects.filter(date_created__date__gte=start_date, date_created__date__lte=end_date)

    # Calculate totals
    totals = transactions.values('transaction_type').annotate(total=Sum('amount'))
    total_income = sum(entry['total'] for entry in totals if entry['transaction_type'] == "Income")
    total_expenses = sum(entry['total'] for entry in totals if entry['transaction_type'] == "Expense")

    # Calculate net balance
    net_balance = total_income - total_expenses

    # Convert transactions into a dictionary list
    transaction_list = [
        {
            "date_created": txn.date_created.strftime("%Y-%m-%d"),
            "transaction_type": txn.transaction_type,
            "category": txn.category,
            "amount": float(txn.amount)
        }
        for txn in transactions
    ]

    # Pass the results to the template
    context = {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_balance": net_balance,
        "transactions": transaction_list,  # Passing as a proper dictionary list
    }
    return render(request, "reports.html", context)