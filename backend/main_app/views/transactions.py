"""BudgetWise transactions views — split from the tested Django application.
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
def transactions(request):
    budgets,incomes,expenses,_,_=summary(request.user)
    rows=activity_items(incomes,expenses)
    search=request.GET.get('q','').strip().lower()
    kind=request.GET.get('type','all')
    if search:
        rows=[r for r in rows if search in (r['name']+' '+r['category']+' '+(r['budget'].budget_name if r['budget'] else '')).lower()]
    if kind in ('income','expense'):
        rows=[r for r in rows if r['kind']==kind]
    return render(request,'budgets/transactions.html',{'section':'transactions','activity':rows,'q':search,'type':kind,'budgets':budgets})


@login_required
def export_csv(request):
    _,incomes,expenses,_,_=summary(request.user)
    response=HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachment; filename="budget-manager-transactions.csv"'
    writer=csv.writer(response)
    writer.writerow(['Type','Description','Amount','Category','Date','Budget'])
    for item in activity_items(incomes,expenses):
        writer.writerow([item['kind'],item['name'],str(item['amount']),item['category'],item['date'].isoformat() if item['date'] else '',item['budget'].budget_name if item['budget'] else ''])
    return response
