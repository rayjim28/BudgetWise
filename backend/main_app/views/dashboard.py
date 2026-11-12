"""BudgetWise dashboard views — split from the tested Django application.
The original URL names, models and permissions are unchanged."""

import csv
from datetime import date
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from ..forms import BudgetForm, ExpenseForm, IncomeForm
from ..models import PersonalBudget, ExpenseItem, Income

from .common import ZERO, owned_budget, owned_expense, owned_income, summary, budget_rows, activity_items

@login_required
def dashboard(request):
    budgets, incomes, expenses, income, spent = summary(request.user)
    rows = budget_rows(budgets)
    recent = activity_items(incomes, expenses, 6)
    categories = []
    category_names = dict(ExpenseItem.EXPENSE_CATEGORIES)
    for key, label in ExpenseItem.EXPENSE_CATEGORIES:
        amount = expenses.filter(item_category=key).aggregate(s=Sum('item_cost'))['s'] or ZERO
        if amount:
            categories.append({'name': label, 'amount': amount, 'pct': min(100, round(float(amount/spent*100))) if spent else 0})
    # Monthly trends include dated expenses. The original Income model has no date field.
    from django.utils import timezone
    today = timezone.localdate()
    trend = []
    for offset in range(5,-1,-1):
        index = today.year*12+today.month-1-offset
        year, month_index = divmod(index, 12)
        mo = month_index+1
        cost = expenses.filter(purchase_date__year=year,purchase_date__month=mo).aggregate(s=Sum('item_cost'))['s'] or ZERO
        trend.append({'label': date(year,mo,1).strftime('%b'), 'amount': cost})
    top = max([t['amount'] for t in trend] + [ZERO])
    for item in trend:
        item['height'] = max(2, round(float(item['amount'] / top * 100))) if top else 2
    # Render a category donut using only real user-scoped spending totals.
    # SVG path lengths add up to 100; no model or migration changes needed.
    has_monthly_expenses = any(item['amount'] for item in trend)
    donut_segments = []
    cumulative = 0.0
    donut_colors = ('#2fe8b8', '#c8ec74', '#38a7c7', '#edab67')
    if spent:
        for index, item in enumerate(categories):
            share = float(item['amount'] / spent * 100)
            if share <= 0:
                continue
            donut_segments.append({
                'name': item['name'], 'pct': item['pct'],
                'size': f'{share:.4f}', 'offset': f'{-cumulative:.4f}',
                'color': donut_colors[index % len(donut_colors)],
            })
            cumulative += share
    # Genuine month-by-month comparison of current vs previous calendar year.
    # Only dated expense records are used; income has no historical dates.
    from calendar import month_abbr
    from django.utils import timezone
    compare_year = timezone.localdate().year
    previous_year = compare_year - 1
    by_month = {
        (entry['purchase_date__year'], entry['purchase_date__month']): entry['total']
        for entry in (
            expenses.filter(purchase_date__year__in=(compare_year, previous_year))
            .values('purchase_date__year', 'purchase_date__month')
            .annotate(total=Sum('item_cost'))
        )
    }
    highest = max([ZERO, *by_month.values()])
    year_compare = []
    for month in range(1, 13):
        this_year = by_month.get((compare_year, month), ZERO)
        last_year = by_month.get((previous_year, month), ZERO)
        year_compare.append({
            'label': month_abbr[month],
            'current_amount': this_year,
            'previous_amount': last_year,
            'current_height': max(3, round(float(this_year / highest * 100))) if this_year and highest else 0,
            'previous_height': max(3, round(float(last_year / highest * 100))) if last_year and highest else 0,
        })
    has_year_expenses = any(item['current_amount'] or item['previous_amount'] for item in year_compare)
    return render(request, 'budgets/dashboard.html', {'section':'dashboard','total_income':income,'total_expenses':spent,'balance':income-spent,'budget_rows':rows[:5],'budget_count':budgets.count(),'recent':recent,'categories':categories,'trend':trend,'donut_segments':donut_segments,'has_monthly_expenses':has_monthly_expenses,'year_compare':year_compare,'has_year_expenses':has_year_expenses,'compare_year':compare_year,'previous_year':previous_year})
