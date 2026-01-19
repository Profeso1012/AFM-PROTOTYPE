# accounts/views.py
from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.views import LoginView, TemplateView, LogoutView
from .forms import CustomUserCreationForm, CustomLoginForm
from .models import CustomUser, SubscriptionPlan
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
import json
from datetime import datetime, timedelta
import requests


class SignupPageView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class CustomLoginView(LoginView):
    authentication_form = CustomLoginForm
    template_name = "registration/login.html"


class ProfilePageView(LoginRequiredMixin, TemplateView):
    template_name = "profile.html"
    login_url = reverse_lazy("login")


class SettingsPageView(LoginRequiredMixin, TemplateView):
    template_name = "settings.html"
    login_url = reverse_lazy("login")

    def post(self, request, *args, **kwargs):
        user = request.user
        action = request.POST.get('action')

        if action == 'update_picture':
            profile_picture = request.FILES.get('profile_picture')
            if profile_picture:
                user.profile_picture = profile_picture
                user.save()
                messages.success(request, "Profile picture updated successfully!")
        
        elif action == 'update_info':
            full_name = request.POST.get('full_name')
            email = request.POST.get('email')
            age = request.POST.get('age')
            
            if full_name:
                user.full_name = full_name
            if email and email != user.email:
                # Check if email already exists
                if CustomUser.objects.filter(email=email).exclude(pk=user.pk).exists():
                    messages.error(request, "This email is already in use.")
                    return redirect('settings')
                user.email = email
            if age:
                user.age = int(age)
            
            user.save()
            messages.success(request, "Profile information updated successfully!")

        return redirect('settings')


class CheckoutView(LoginRequiredMixin, generic.TemplateView):
    template_name = "checkout.html"
    login_url = reverse_lazy("login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tier = self.kwargs.get('tier')
        plan = get_object_or_404(SubscriptionPlan, tier=tier)
        context['plan'] = plan
        return context

    def post(self, request, *args, **kwargs):
        tier = self.kwargs.get('tier')
        plan = get_object_or_404(SubscriptionPlan, tier=tier)
        phone = request.POST.get('phone')
        duration = int(request.POST.get('duration', 1))
        terms = request.POST.get('terms')

        if not terms:
            messages.error(request, "You must accept the terms and conditions.")
            return redirect('checkout', tier=tier)

        if not phone:
            messages.error(request, "Phone number is required.")
            return redirect('checkout', tier=tier)

        # Calculate total amount (with discount for longer billing cycles)
        amount = float(plan.price_monthly) * duration
        if duration == 3:
            amount = amount * 0.95  # 5% discount
        elif duration == 6:
            amount = amount * 0.90  # 10% discount
        elif duration == 12:
            amount = amount * 0.85  # 15% discount

        # Initialize Paystack transaction
        try:
            paystack_ref = self._initialize_paystack_transaction(
                request.user.email,
                int(amount * 100),  # Paystack uses kobo
                request.user.full_name,
                phone,
                tier,
                duration
            )
            
            if paystack_ref:
                # Store transaction info in session
                request.session['pending_subscription'] = {
                    'tier': tier,
                    'duration': duration,
                    'amount': float(amount),
                    'paystack_reference': paystack_ref
                }
                
                # Redirect to Paystack payment
                return redirect(f'https://checkout.paystack.com/{paystack_ref}')
            else:
                messages.error(request, "Failed to initiate payment. Please try again.")
                return redirect('checkout', tier=tier)
                
        except Exception as e:
            messages.error(request, f"Payment error: {str(e)}")
            return redirect('checkout', tier=tier)

    def _initialize_paystack_transaction(self, email, amount, name, phone, tier, duration):
        """Initialize Paystack transaction and return reference"""
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json'
        }
        
        url = 'https://api.paystack.co/transaction/initialize'
        data = {
            "email": email,
            "amount": amount,
            "metadata": {
                "full_name": name,
                "phone": phone,
                "subscription_tier": tier,
                "duration_months": duration
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json()['data']['reference']
            return None
        except Exception as e:
            print(f"Paystack error: {e}")
            return None


class PaymentVerificationView(LoginRequiredMixin, TemplateView):
    """Handle payment verification and subscription activation"""
    
    def get(self, request, *args, **kwargs):
        reference = request.GET.get('reference')
        
        if not reference:
            messages.error(request, "Invalid payment reference.")
            return redirect('profile')

        # Verify transaction with Paystack
        verified = self._verify_paystack_transaction(reference)
        
        if verified:
            pending = request.session.get('pending_subscription')
            if pending:
                user = request.user
                tier = pending['tier']
                duration = pending['duration']
                
                # Update user subscription
                user.subscription_tier = tier
                user.is_subscribed = True
                user.subscription_start_date = datetime.now()
                user.subscription_end_date = datetime.now() + timedelta(days=30 * duration)
                user.save()
                
                # Clean up session
                del request.session['pending_subscription']
                
                messages.success(request, f"Welcome to {tier.capitalize()} tier! Your subscription is now active.")
                return redirect('profile')
        
        messages.error(request, "Payment verification failed.")
        return redirect('profile')

    def _verify_paystack_transaction(self, reference):
        """Verify transaction with Paystack"""
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'
        }
        
        url = f'https://api.paystack.co/transaction/verify/{reference}'
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return data['data']['status'] == 'success'
            return False
        except Exception as e:
            print(f"Verification error: {e}")
            return False


class ManageSubscriptionView(LoginRequiredMixin, TemplateView):
    template_name = "manage_subscription.html"
    login_url = reverse_lazy("login")


class DowngradeSubscriptionView(LoginRequiredMixin, generic.View):
    def get(self, request, tier):
        user = request.user
        user.subscription_tier = tier
        if tier == 'free':
            user.is_subscribed = False
            user.subscription_end_date = None
        user.save()
        messages.success(request, "Subscription updated successfully.")
        return redirect('profile')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("home")  # Redirect to home page after logout
    http_method_names = ['get', 'post']
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "You have been logged out successfully.")
        return super().dispatch(request, *args, **kwargs)
