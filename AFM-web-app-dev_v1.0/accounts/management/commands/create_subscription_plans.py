from django.core.management.base import BaseCommand
from accounts.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Create default subscription plans'

    def handle(self, *args, **options):
        plans = [
            {
                'name': 'Free',
                'tier': 'free',
                'price_monthly': 0,
                'description': 'Perfect for getting started with financial literacy',
                'features': [
                    'Access to market news',
                    'Financial literacy articles',
                    'Basic stock profiles',
                    'Community forum access',
                ]
            },
            {
                'name': 'Basic - WhatsApp Group Access',
                'tier': 'basic',
                'price_monthly': 5000,
                'description': 'Join our exclusive WhatsApp community for market insights',
                'features': [
                    'WhatsApp group access',
                    'Daily market updates',
                    'Buy/sell recommendations',
                    'Financial tips & habits',
                    'Weekly quizzes',
                    'Access to market news',
                    'Financial literacy articles',
                ]
            },
            {
                'name': 'Premium - Personal Sessions',
                'tier': 'premium',
                'price_monthly': 15000,
                'description': 'Get personalized guidance from our financial experts',
                'features': [
                    'All Basic features',
                    'Monthly personal sessions',
                    'Priority email support',
                    'Advanced analytics',
                    'Custom reports',
                    'Portfolio analysis',
                ]
            },
            {
                'name': 'Elite - VIP Support',
                'tier': 'elite',
                'price_monthly': 50000,
                'description': 'Ultimate investment management experience',
                'features': [
                    'All Premium features',
                    'Weekly expert sessions',
                    'Dedicated account manager',
                    'Portfolio review & strategy',
                    '24/7 VIP support',
                    'Direct access to analysts',
                    'Custom investment strategy',
                ]
            },
        ]

        for plan_data in plans:
            plan, created = SubscriptionPlan.objects.get_or_create(
                tier=plan_data['tier'],
                defaults={
                    'name': plan_data['name'],
                    'price_monthly': plan_data['price_monthly'],
                    'description': plan_data['description'],
                    'features': plan_data['features'],
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created plan: {plan.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Plan already exists: {plan.name}')
                )
