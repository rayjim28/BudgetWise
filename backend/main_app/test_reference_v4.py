"""Check the new dashboard comparison uses only stored, user-owned expenses."""
from datetime import date
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import PersonalBudget, ExpenseItem


class YearComparisonDashboardTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('comparison_owner', password='TestPass-892!')
        self.other = User.objects.create_user('comparison_other', password='TestPass-892!')
        self.budget = PersonalBudget.objects.create(owner=self.user, budget_name='My budget')
        other_budget = PersonalBudget.objects.create(owner=self.other, budget_name='Other budget')
        year = timezone.localdate().year
        ExpenseItem.objects.create(owner=self.user, budget=self.budget, item_name='Current', item_cost=Decimal('125.00'), item_category='🛒', purchase_date=date(year, 1, 10))
        ExpenseItem.objects.create(owner=self.user, budget=self.budget, item_name='Prior', item_cost=Decimal('70.00'), item_category='🏠', purchase_date=date(year-1, 1, 10))
        ExpenseItem.objects.create(owner=self.other, budget=other_budget, item_name='Private', item_cost=Decimal('900.00'), item_category='🏠', purchase_date=date(year, 1, 10))

    def test_yearly_expense_bars_are_user_scoped(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        jan = response.context['year_compare'][0]
        self.assertEqual(jan['current_amount'], Decimal('125.00'))
        self.assertEqual(jan['previous_amount'], Decimal('70.00'))
        self.assertTrue(response.context['has_year_expenses'])
        self.assertEqual(len(response.context['year_compare']), 12)
        self.assertNotContains(response, '900.00')

    def test_no_expenses_shows_empty_state(self):
        clean = User.objects.create_user('clean_comparison_owner', password='TestPass-892!')
        self.client.force_login(clean)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['has_year_expenses'])
        self.assertContains(response, 'No recorded spending for these years yet')
