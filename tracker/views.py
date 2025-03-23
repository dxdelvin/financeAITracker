from django.shortcuts import render, redirect, get_object_or_404
from .models import Transaction
from .forms import TransactionForm
from django.utils import timezone
from django.contrib import messages
from .ai_processor import TransactionParser
from datetime import timedelta
from django.db.models import Sum

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
            # Existing form handling remains same
            pass

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
    # Get filter parameters
    filter_type = request.GET.get('type', '7')
    start_date, end_date = get_date_range(filter_type, request)

    # Filter transactions
    transactions = Transaction.objects.filter(
        date_created__range=(start_date, end_date))

    # Calculate metrics
    total_income = transactions.filter(transaction_type='Income').aggregate(
        Sum('amount'))['amount__sum'] or 0
    total_expenses = transactions.filter(transaction_type='Expense').aggregate(
        Sum('amount'))['amount__sum'] or 0

    # Prepare chart data
    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_balance': total_income - total_expenses,
        'categories': list(transactions.values_list('category', flat=True).distinct()),
        'category_amounts': list(transactions.values('category').annotate(
            total=Sum('amount')).values_list('total', flat=True)),
        'months': ["Jan", "Feb", "Mar"],  # Replace with actual month data
        'monthly_income': [0, 0, 0],  # Replace with actual data
        'monthly_expenses': [0, 0, 0]  # Replace with actual data
    }
    return render(request, 'reports.html', context)


def get_date_range(filter_type, request):
    today = timezone.now().date()

    date_map = {
        '7': (today - timedelta(days=7), today),
        '30': (today - timedelta(days=30), today),
        '365': (today - timedelta(days=365), today),
        'thismonth': (today.replace(day=1), today),
        'thisyear': (today.replace(month=1, day=1), today),
        'custom': (
            request.GET.get('start', today),
            request.GET.get('end', today)
        )
    }
    return date_map.get(filter_type, (today - timedelta(days=7), today))