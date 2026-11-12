"""BudgetWise budgets views — split from the tested Django application.
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
def index(request):
    budgets, _, _, _, _ = summary(request.user)
    return render(request, 'budgets/index.html', {'section':'budgets','budget_data':budget_rows(budgets)})


@login_required
def create(request):
    form = BudgetForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        budget=form.save(commit=False)
        budget.owner=request.user
        budget.save()
        messages.success(request, 'Budget created.')
        return redirect('detail',budget_id=budget.pk)
    return render(request,'budgets/create.html',{'section':'budgets','form':form})


@login_required
def detail(request,budget_id):
    budget=owned_budget(request,budget_id)
    row=budget_rows([budget])[0]
    incomes=Income.objects.filter(budget=budget,owner=request.user).order_by('-pk')
    expenses=ExpenseItem.objects.filter(budget=budget,owner=request.user).order_by('-purchase_date','-pk')
    return render(request,'budgets/detail.html',{'section':'budgets','budget':budget,'row':row,'incomes':incomes[:6],'expenses':expenses[:6]})


@login_required
def edit(request,budget_id):
    budget=owned_budget(request,budget_id)
    form=BudgetForm(request.POST or None,instance=budget)
    if request.method=='POST' and form.is_valid():
        form.save()
        messages.success(request, 'Budget updated.')
        return redirect('detail',budget_id=budget.pk)
    return render(request,'budgets/edit.html',{'section':'budgets','budget':budget,'form':form})


@login_required
@require_POST
def delete(request,budget_id):
    budget=owned_budget(request,budget_id)
    budget.delete()
    messages.success(request, 'Budget deleted.')
    return redirect('index')
