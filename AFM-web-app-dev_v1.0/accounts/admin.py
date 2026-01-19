# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, SubscriptionPlan
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ("email", "full_name", "age", "subscription_tier", "is_subscribed", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "subscription_tier", "is_subscribed")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("full_name", "age", "profile_picture")}),
        ("Subscription", {"fields": ("subscription_tier", "is_subscribed", "subscription_start_date", "subscription_end_date", "paystack_customer_code")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "full_name", "age", "password1", "password2", "is_staff", "is_active"),
        }),
    )
    search_fields = ("email", "full_name")
    ordering = ("email",)

class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "tier", "price_monthly")
    list_filter = ("tier",)
    search_fields = ("name", "tier")
    ordering = ("price_monthly",)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)