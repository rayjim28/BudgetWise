"""BudgetWise expenses views — split from the tested Django application.
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
def create_expense(request,budget_id):
    budget=owned_budget(request,budget_id)
    form=ExpenseForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        expense=form.save(commit=False)
        expense.owner=request.user
        expense.budget=budget
        expense.save()
        messages.success(request, 'Expense added.')
        return redirect('expense_list',budget_id=budget.pk)
    return render(request,'budgets/expenses/create_expense.html',{'section':'transactions','budget':budget,'form':form})


@login_required
def expense_list(request,budget_id):
    budget=owned_budget(request,budget_id)
    expenses=ExpenseItem.objects.filter(budget=budget,owner=request.user).order_by('-purchase_date','-pk')
    return render(request,'budgets/expenses/expense_list.html',{'section':'transactions','budget':budget,'expenses':expenses,'total_spent':expenses.aggregate(s=Sum('item_cost'))['s'] or ZERO})


@login_required
def expense_detail(request,budget_id,expense_id):
    budget=owned_budget(request,budget_id)
    expense=owned_expense(request,budget,expense_id)
    return render(request,'budgets/expenses/expense_detail.html',{'section':'transactions','budget':budget,'expense':expense})


@login_required
def expense_edit(request,budget_id,expense_id):
    budget=owned_budget(request,budget_id)
    expense=owned_expense(request,budget,expense_id)
    form=ExpenseForm(request.POST or None,instance=expense)
    if request.method=='POST' and form.is_valid():
        form.save()
        messages.success(request,'Expense updated.')
        return redirect('expense_list',budget_id=budget.pk)
    return render(request,'budgets/expenses/expense_edit.html',{'section':'transactions','budget':budget,'expense':expense,'form':form})


@login_required
@require_POST
def expense_delete(request,budget_id,expense_id):
    budget=owned_budget(request,budget_id)
    owned_expense(request,budget,expense_id).delete()
    messages.success(request, 'Expense deleted.')
    return redirect('expense_list',budget_id=budget.pk)
