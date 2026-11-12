"""BudgetWise incomes views — split from the tested Django application.
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
def income_list(request,budget_id):
    budget=owned_budget(request,budget_id)
    incomes=Income.objects.filter(budget=budget,owner=request.user).order_by('-pk')
    return render(request,'budgets/incomes/income_list.html',{'section':'transactions','budget':budget,'incomes':incomes,'total_income':incomes.aggregate(s=Sum('amount'))['s'] or ZERO})


@login_required
def create_income(request,budget_id):
    budget=owned_budget(request,budget_id)
    form=IncomeForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        item=form.save(commit=False)
        item.owner=request.user
        item.budget=budget
        item.save()
        messages.success(request,'Income added.')
        return redirect('income_list',budget_id=budget.pk)
    return render(request,'budgets/incomes/create_income.html',{'section':'transactions','budget':budget,'form':form})


@login_required
def income_detail(request,budget_id,income_id):
    budget=owned_budget(request,budget_id)
    income=owned_income(request,budget,income_id)
    return render(request,'budgets/incomes/income_detail.html',{'section':'transactions','budget':budget,'income':income})


@login_required
def income_edit(request,budget_id,income_id):
    budget=owned_budget(request,budget_id)
    income=owned_income(request,budget,income_id)
    form=IncomeForm(request.POST or None,instance=income)
    if request.method=='POST' and form.is_valid():
        form.save()
        messages.success(request,'Income updated.')
        return redirect('income_list',budget_id=budget.pk)
    return render(request,'budgets/incomes/income_edit.html',{'section':'transactions','budget':budget,'income':income,'form':form})


@login_required
def income_delete(request,budget_id,income_id):
    budget=owned_budget(request,budget_id)
    income=owned_income(request,budget,income_id)
    if request.method=='POST':
        income.delete()
        messages.success(request,'Income deleted.')
        return redirect('income_list',budget_id=budget.pk)
    return render(request,'budgets/incomes/income_confirm_delete.html',{'section':'transactions','budget':budget,'income':income})
