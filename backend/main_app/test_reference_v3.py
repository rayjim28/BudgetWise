"""Regression checks for the dashboard redesign. Uses Django's isolated test database."""
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import PersonalBudget, ExpenseItem, Income


class BudgetWiseReferenceV3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='v3-test-account', password='Test-only-strong-password-2026!'
        )
        self.client.force_login(self.user)

    def test_empty_dashboard_stays_truthful(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No expenses recorded yet')
        self.assertContains(response, 'No spending categories yet')
        self.assertContains(response, 'Recent transactions')
        self.assertContains(response, 'Budget health')
        self.assertEqual(response.context['donut_segments'], [])

    def test_spending_donut_uses_real_database_values(self):
        budget = PersonalBudget.objects.create(owner=self.user, budget_name='Test budget')
        Income.objects.create(owner=self.user, budget=budget, name='Test income', amount=Decimal('200.00'))
        ExpenseItem.objects.create(
            owner=self.user, budget=budget, item_name='Test groceries',
            item_cost=Decimal('75.00'), item_category='🛒', purchase_date=date(2026, 11, 2)
        )
        ExpenseItem.objects.create(
            owner=self.user, budget=budget, item_name='Test housing',
            item_cost=Decimal('25.00'), item_category='🏠', purchase_date=date(2026, 11, 3)
        )
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Spending categories')
        self.assertContains(response, 'Test groceries')
        segments = response.context['donut_segments']
        self.assertEqual(len(segments), 2)
        self.assertAlmostEqual(sum(float(s['size']) for s in segments), 100, delta=0.02)
        self.assertContains(response, '$100.00')
