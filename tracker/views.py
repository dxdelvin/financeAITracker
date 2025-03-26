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
    # Default filter: last 7 days
    days = request.GET.get('days')
    start_date = None
    end_date = date.today()

    # Custom date range
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
            start_date = end_date.replace(month=1, day=1)
        elif days == "7":
            start_date = end_date - timedelta(days=7)
        elif days == "30":
            start_date = end_date - timedelta(days=30)
        elif days == "365":
            start_date = end_date - timedelta(days=365)
        else:
            # default fallback
            start_date = end_date - timedelta(days=7)
    else:
        start_date = end_date - timedelta(days=7)

    # Filter transactions based on the selected date range
    transactions = Transaction.objects.filter(date_created__date__gte=start_date, date_created__date__lte=end_date)

    # Calculate totals for income and expenses
    totals = transactions.values('transaction_type').annotate(total=Sum('amount'))
    total_income = 0
    total_expenses = 0
    for entry in totals:
        if entry['transaction_type'] == "Income":
            total_income = entry['total'] or 0
        elif entry['transaction_type'] == "Expense":
            total_expenses = entry['total'] or 0

    net_balance = total_income - total_expenses

    # Group transactions by category (for expenses only or all transactions as needed)
    category_data = transactions.filter(transaction_type="Expense").values('category').annotate(total=Sum('amount'))
    categories = []
    category_amounts = []
    for item in category_data:
        categories.append(item['category'])
        category_amounts.append(float(item['total'] or 0))

    # Aggregate monthly income and expenses for trend chart
    monthly_data = transactions.annotate(month=TruncMonth('date_created')).values('month', 'transaction_type').annotate(
        total=Sum('amount')).order_by('month')

    # Prepare dictionaries to accumulate monthly values
    monthly_income_dict = {}
    monthly_expenses_dict = {}

    for entry in monthly_data:
        month_str = entry['month'].strftime("%B %Y")
        if entry['transaction_type'] == "Income":
            monthly_income_dict[month_str] = float(entry['total'] or 0)
        else:
            monthly_expenses_dict[month_str] = float(entry['total'] or 0)

    # Create a sorted list of months within the date range
    months_set = set(list(monthly_income_dict.keys()) + list(monthly_expenses_dict.keys()))
    months = sorted(months_set, key=lambda d: datetime.strptime(d, "%B %Y"))

    monthly_income = [monthly_income_dict.get(m, 0) for m in months]
    monthly_expenses = [monthly_expenses_dict.get(m, 0) for m in months]

    context = {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_balance": net_balance,
        "categories_json": categories,
        "category_amounts_json": category_amounts,
        "months_json": months,
        "monthly_income_json": monthly_income,
        "monthly_expenses_json": monthly_expenses,
    }
    return render(request, "reports.html", context)