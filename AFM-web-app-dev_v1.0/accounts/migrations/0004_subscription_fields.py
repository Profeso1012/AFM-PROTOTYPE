# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_customuser_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='subscription_tier',
            field=models.CharField(
                choices=[
                    ('free', 'Free'),
                    ('basic', 'Basic - WhatsApp Group Access'),
                    ('premium', 'Premium - Personal Sessions'),
                    ('elite', 'Elite - VIP Support & Expert Sessions'),
                ],
                default='free',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_subscribed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='subscription_start_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='subscription_end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='paystack_customer_code',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.CreateModel(
            name='SubscriptionPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('tier', models.CharField(
                    choices=[
                        ('free', 'Free'),
                        ('basic', 'Basic - WhatsApp Group Access'),
                        ('premium', 'Premium - Personal Sessions'),
                        ('elite', 'Elite - VIP Support & Expert Sessions'),
                    ],
                    max_length=20,
                )),
                ('price_monthly', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.TextField()),
                ('features', models.JSONField(default=list)),
            ],
            options={
                'ordering': ['price_monthly'],
            },
        ),
    ]
