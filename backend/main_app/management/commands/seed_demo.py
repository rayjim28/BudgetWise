"""Create illustrative records ONLY for an existing user in the isolated local V2 SQLite DB."""
from datetime import date
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from backend.main_app.models import ExpenseItem, Income, PersonalBudget


class Command(BaseCommand):
    help = 'Populate an empty local-v2.sqlite3 test account with sample budgets and expenses.'

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True, help='An existing account in the local test DB')

    def handle(self, *args, **options):
        database = settings.DATABASES['default']
        if not settings.DEBUG or database['ENGINE'] != 'django.db.backends.sqlite3' or Path(database['NAME']).name != 'local-v2.sqlite3':
            raise CommandError('This command can run only in DEBUG mode against local-v2.sqlite3.')
        username = options['username']
        user = get_user_model().objects.filter(username=username).first()
        if not user:
            raise CommandError('User not found. Create an account at /signup/ first.')
        if PersonalBudget.objects.filter(owner=user).exists() or ExpenseItem.objects.filter(owner=user).exists() or Income.objects.filter(owner=user).exists():
            raise CommandError('Account already has records; refusing to mix sample and real data.')

        everyday = PersonalBudget.objects.create(owner=user, budget_name='Everyday expenses')
        home = PersonalBudget.objects.create(owner=user, budget_name='Home and essentials')
        goals = PersonalBudget.objects.create(owner=user, budget_name='Savings plan')
        for budget, name, amount in [(everyday, 'Primary income', '3150.00'),(home, 'Household income', '1750.00'),(goals, 'Side project', '575.00')]:
            Income.objects.create(owner=user, budget=budget, name=name, amount=Decimal(amount))
        base = timezone.localdate()
        demo = [
            ('Groceries', '🛒', '210.40', everyday),
            ('Household supplies', '🏠', '460.00', home),
            ('Car fuel', '🚙', '145.85', everyday),
            ('Medical visit', '🏥', '105.00', home),
            ('Grocery shopping', '🛒', '280.75', everyday),
            ('Rent contribution', '🏠', '895.00', home),
            ('Car maintenance', '🚙', '190.00', everyday),
            ('Weekly groceries', '🛒', '160.20', everyday),
            ('Home expenses', '🏠', '530.00', home),
            ('Pharmacy', '🏥', '76.00', home),
            ('Fuel', '🚙', '112.90', everyday),
            ('Food and essentials', '🛒', '198.55', everyday),
        ]
        for i,(name,category,amount,budget) in enumerate(demo):
            offset = i // 2
            month_index = base.year * 12 + base.month - 1 - offset
            year, month0 = divmod(month_index, 12)
            day = min(12 + (i%2)*8,28)
            ExpenseItem.objects.create(owner=user,budget=budget,item_name=name,item_category=category,
                                       item_cost=Decimal(amount),purchase_date=date(year,month0+1,day))
        self.stdout.write(self.style.SUCCESS('Added illustrative local demo data. Never use this database for production.'))
