from django.contrib import admin
from .models import User, Consent, Subscription, Payment, HelpSection, Feedback, SubscriptionStatistics

# User modeli uchun admin interfeysni sozlash
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'name', 'username', 'registration_time')
    search_fields = ('user_id', 'name', 'username')
    list_filter = ('registration_time',)

# Consent modeli uchun admin interfeysni sozlash
@admin.register(Consent)
class ConsentAdmin(admin.ModelAdmin):
    list_display = ('user', 'consent_given', 'consent_date')
    list_filter = ('consent_given', 'consent_date')

# Subscription modeli uchun admin interfeysni sozlash
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'start_date', 'end_date', 'is_active')
    search_fields = ('user__name', 'plan')
    list_filter = ('plan', 'is_active', 'start_date', 'end_date')

# Payment modeli uchun admin interfeysni sozlash
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_method', 'payment_date')
    search_fields = ('user__name', 'payment_method', 'transaction_id')
    list_filter = ('payment_method', 'payment_date')

# HelpSection modeli uchun admin interfeysni sozlash
@admin.register(HelpSection)
class HelpSectionAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)

# Feedback modeli uchun admin interfeysni sozlash
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at')
    search_fields = ('user__name', 'message')
    list_filter = ('created_at',)

# SubscriptionStatistics modeli uchun admin interfeysni sozlash
@admin.register(SubscriptionStatistics)
class SubscriptionStatisticsAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_payments', 'subscription_count', 'last_payment_date')
    search_fields = ('user__name',)
    list_filter = ('last_payment_date',)
