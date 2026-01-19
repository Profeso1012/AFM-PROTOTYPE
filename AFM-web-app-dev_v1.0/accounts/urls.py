# accounts/urls.py
import os
from django.urls import path
from .views import (
    SignupPageView, CustomLoginView, ProfilePageView, CustomLogoutView,
    SettingsPageView, CheckoutView, PaymentVerificationView,
    ManageSubscriptionView, DowngradeSubscriptionView
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("signup/", SignupPageView.as_view(), name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("profile/", ProfilePageView.as_view(), name="profile"),
    path("settings/", SettingsPageView.as_view(), name="settings"),
    path("checkout/<str:tier>/", CheckoutView.as_view(), name="checkout"),
    path("payment/verify/", PaymentVerificationView.as_view(), name="payment_verify"),
    path("subscription/manage/", ManageSubscriptionView.as_view(), name="manage_subscription"),
    path("subscription/downgrade/<str:tier>/", DowngradeSubscriptionView.as_view(), name="downgrade_subscription"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)