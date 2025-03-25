from django.shortcuts import render, redirect, get_object_or_404
from .models import Transaction
from .forms import TransactionForm
from django.utils import timezone
from django.contrib import messages
from .ai_processor import TransactionParser
from datetime import timedelta
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import datetime
import json
from django.core.serializers.json import DjangoJSONEncoder

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
    # Get filter parameters
    filter_type = request.GET.get('type', '7')
    start_date, end_date = get_date_range(filter_type, request)

    # Filter transactions based on date range
    transactions = Transaction.objects.filter(date_created__range=(start_date, end_date))

    # Calculate totals using aggregation
    total_income = float(transactions.filter(transaction_type='Income')
                         .aggregate(Sum('amount'))['amount__sum'] or 0.00)
    total_expenses = float(transactions.filter(transaction_type='Expense')
                           .aggregate(Sum('amount'))['amount__sum'] or 0.00)

    # Category Breakdown
    category_data = transactions.values('category').annotate(total=Sum('amount')).order_by('category')

    # Monthly Trends
    monthly_data = transactions.annotate(
        month=TruncMonth('date_created')
    ).values('month', 'transaction_type').annotate(
        total=Sum('amount')
    ).order_by('month')

    # Prepare data for charts
    months = sorted(list(set(item['month'] for item in monthly_data)))
    monthly_income = [
        next((item['total'] for item in monthly_data
              if item['month'] == month and item['transaction_type'] == 'Income'), 0)
        for month in months
    ]
    monthly_expenses = [
        next((item['total'] for item in monthly_data
              if item['month'] == month and item['transaction_type'] == 'Expense'), 0)
        for month in months
    ]

    # Format months for display
    formatted_months = [month.strftime('%b %Y') for month in months]
    default_data = {
        'categories': ['No Data'],
        'category_amounts': [0],
        'months': [timezone.now().strftime('%b %Y')],
        'monthly_income': [0],
        'monthly_expenses': [0]
    }
    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_balance': total_income - total_expenses,
        'categories': json.dumps(
            [item['category'] for item in category_data] if category_data else default_data['categories'],
            cls=DjangoJSONEncoder
        ),
        'category_amounts': json.dumps(
            [float(item['total']) for item in category_data] if category_data else default_data['category_amounts'],
            cls=DjangoJSONEncoder
        ),
        'months': json.dumps(
            formatted_months or ['No Data'],
            cls=DjangoJSONEncoder
        ),
        'monthly_income': json.dumps(
            monthly_income or [0],
            cls=DjangoJSONEncoder
        ),
        'monthly_expenses': json.dumps(
            monthly_expenses or [0],
            cls=DjangoJSONEncoder
        ),
    }
    return render(request, 'reports.html', context)


def get_date_range(filter_type, request):
    today = timezone.now().date()
    try:
        if filter_type == 'custom':
            start = datetime.strptime(request.GET.get('start'), '%Y-%m-%d').date()
            end = datetime.strptime(request.GET.get('end'), '%Y-%m-%d').date()
            return (start, end)

        date_map = {
            '7': (today - timedelta(days=7), today),
            '30': (today - timedelta(days=30), today),
            '365': (today - timedelta(days=365), today),
            'thismonth': (today.replace(day=1), today),
            'thisyear': (today.replace(month=1, day=1), today),
        }
        return date_map.get(filter_type, (today - timedelta(days=7), today))
    except (ValueError, TypeError):
        return (today - timedelta(days=7), today)