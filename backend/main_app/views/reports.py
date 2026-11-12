"""BudgetWise reports views — split from the tested Django application.
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
def reports(request):
    _,incomes,expenses,total_income,total_expenses=summary(request.user)
    categories=[]
    for category,label in ExpenseItem.EXPENSE_CATEGORIES:
        amount=expenses.filter(item_category=category).aggregate(s=Sum('item_cost'))['s'] or ZERO
        categories.append({'name':label,'amount':amount,'pct':min(100,round(float(amount / total_expenses * 100))) if total_expenses else 0})
    return render(request,'budgets/reports.html',{'section':'reports','income':total_income,'spent':total_expenses,'balance':total_income-total_expenses,'categories':categories})
