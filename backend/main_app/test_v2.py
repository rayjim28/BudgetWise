"""Regression checks for BudgetWise V2's new layout and request headers."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class BudgetWiseV2Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='v2-verifier', password='Test-only-strong-password-2026!'
        )

    def test_dashboard_uses_real_data_and_renders_v2_sections(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Available balance')
        self.assertContains(response, 'Spending activity')
        self.assertContains(response, 'No spending categories yet')
        self.assertContains(response, 'Recent transactions')
        self.assertContains(response, 'Budget health')

    def test_budget_and_transaction_views_still_work(self):
        self.client.force_login(self.user)
        for name in ('dashboard', 'index', 'transactions', 'reports'):
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_privacy_headers_and_authentication(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.headers['Permissions-Policy'],
                         'camera=(), microphone=(), geolocation=()')
        self.assertEqual(response.headers['Referrer-Policy'],
                         'strict-origin-when-cross-origin')
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 302)
