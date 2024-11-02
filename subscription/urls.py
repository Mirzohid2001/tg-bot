from django.urls import path
from .views import (
    RegisterView,
    ConsentView,
    SubscriptionView,
    PaymentView,
    SubscriptionStatusView,
    HelpView,
    FeedbackView,
    PaymentCheckView,
    StatisticsView,
    UserProfileView, GiftSubscriptionView, AboutProductView, SupportView,AdviceView,MethodView, SaveCardView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('consent/', ConsentView.as_view(), name='consent'),
    path('subscription/', SubscriptionView.as_view(), name='subscription'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('subscription-status/<str:user_id>/', SubscriptionStatusView.as_view(), name='subscription-status'),
    path('help/', HelpView.as_view(), name='help'),
    path('feedback/', FeedbackView.as_view(), name='feedback'),
    path('payment-check/', PaymentCheckView.as_view(), name='payment-check'),
    path('statistics/<str:user_id>/', StatisticsView.as_view(), name='statistics'),
    path('user-profile/<str:user_id>/', UserProfileView.as_view(), name='user-profile'),
    path('gift/', GiftSubscriptionView.as_view(), name='gift'),
    path('about/', AboutProductView.as_view(), name='about'),
    path('support/', SupportView.as_view(), name='support'),
    path('advice/', AdviceView.as_view(), name='advice'),
    path('method/', MethodView.as_view(), name='method'),
    path('save-card/', SaveCardView.as_view(), name='save-card'),
]
