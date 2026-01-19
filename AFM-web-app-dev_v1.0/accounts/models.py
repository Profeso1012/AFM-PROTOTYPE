# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """Custom manager for CustomUser with email as the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    # Remove the username field
    # username = models.CharField(max_length=150, blank=True)
    username = None
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=70, default="Default Name")
    age = models.PositiveIntegerField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures', null=True, blank=True)
    
    # Subscription fields
    TIER_CHOICES = [
        ('free', 'Free'),
        ('basic', 'Basic - WhatsApp Group Access'),
        ('premium', 'Premium - Personal Sessions'),
        ('elite', 'Elite - VIP Support & Expert Sessions'),
    ]
    subscription_tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='free')
    is_subscribed = models.BooleanField(default=False)
    subscription_start_date = models.DateTimeField(null=True, blank=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    paystack_customer_code = models.CharField(max_length=200, null=True, blank=True)

    USERNAME_FIELD = "email"  # Set email as the unique identifier
    REQUIRED_FIELDS = ["full_name", "age"]  # Fields required when creating a user

    objects = CustomUserManager()  # Link the custom manager
    
    def save(self, *args, **kwargs):
        # If profile picture exists, clean the filename by replacing spaces with underscores
        if self.profile_picture:
            # Sanitize the file name to avoid spaces
            self.profile_picture.name = self.profile_picture.name.replace(' ', '_')
        super().save(*args, **kwargs)


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    tier = models.CharField(max_length=20, choices=CustomUser.TIER_CHOICES)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    features = models.JSONField(default=list)
    
    def __str__(self):
        return f"{self.name} - ${self.price_monthly}/month"
    
    class Meta:
        ordering = ['price_monthly']