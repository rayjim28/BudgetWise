"""BudgetWise common views — split from the tested Django application.
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

ZERO = Decimal('0.00')

def owned_budget(request, budget_id):
    return get_object_or_404(PersonalBudget, pk=budget_id, owner=request.user)


def owned_expense(request, budget, expense_id):
    return get_object_or_404(ExpenseItem, pk=expense_id, owner=request.user, budget=budget)


def owned_income(request, budget, income_id):
    return get_object_or_404(Income, pk=income_id, owner=request.user, budget=budget)


def summary(user):
    budgets = PersonalBudget.objects.filter(owner=user).order_by('-creation_date', '-pk')
    income = Income.objects.filter(owner=user, budget__owner=user)
    expenses = ExpenseItem.objects.filter(owner=user, budget__owner=user)
    total_income = income.aggregate(s=Sum('amount'))['s'] or ZERO
    total_expenses = expenses.aggregate(s=Sum('item_cost'))['s'] or ZERO
    return budgets, income, expenses, total_income, total_expenses


def budget_rows(budgets):
    rows = []
    for budget in budgets:
        received = Income.objects.filter(owner=budget.owner, budget=budget).aggregate(s=Sum('amount'))['s'] or ZERO
        spent = ExpenseItem.objects.filter(owner=budget.owner, budget=budget).aggregate(s=Sum('item_cost'))['s'] or ZERO
        pct = min(100, round(float(spent / received * 100))) if received else 0
        rows.append({'budget': budget, 'income': received, 'spent': spent, 'balance': received-spent, 'pct': pct, 'over': spent > received and received > 0})
    return rows


def activity_items(incomes, expenses, limit=None):
    # Income has no date in the original model; keep it undated instead of inventing one.
    items = [{'name': e.item_name, 'amount': e.item_cost, 'date': e.purchase_date, 'kind': 'expense', 'budget': e.budget, 'pk': e.pk, 'category': e.get_item_category_display()} for e in expenses.select_related('budget')]
    items += [{'name': i.name or 'Income', 'amount': i.amount, 'date': None, 'kind': 'income', 'budget': i.budget, 'pk': i.pk, 'category': 'Income'} for i in incomes.select_related('budget')]
    items.sort(key=lambda x: (x['date'] is not None, x['date'] or date.min, x['pk']), reverse=True)
    return items[:limit] if limit else items
