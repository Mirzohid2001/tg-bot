from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Consent, Subscription, Payment, SubscriptionStatistics, Feedback, HelpSection, Advice, Method, \
    UserCard
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db import models
from .serializers import AdviceSerializer, MethodSerializer, CardSerializer

VALID_PLANS = ["monthly", "yearly"]


def calculate_subscription_end_date(plan):
    """Obuna rejasi bo'yicha muddati hisoblaydi"""
    if plan == "monthly":
        return timezone.now() + timedelta(days=30)
    elif plan == "yearly":
        return timezone.now() + timedelta(days=365)
    return None


class RegisterView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        username = request.data.get('username')

        # Faqat user_id va username'ni tekshiramiz
        if not (user_id and username):
            return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

        # Foydalanuvchi mavjudligini tekshirish
        if User.objects.filter(user_id=user_id).exists():
            return Response({"message": "You are already registered"}, status=status.HTTP_200_OK)

        # Foydalanuvchini ro'yxatdan o'tkazish
        user, created = User.objects.update_or_create(
            user_id=user_id,
            defaults={'username': username}  # Email qo'shilmagan
        )
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)


class ConsentView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        consent_given = request.data.get('consent_given')
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": f"User with ID {user_id} not found"}, status=status.HTTP_404_NOT_FOUND)

        if consent_given is not None:
            consent, created = Consent.objects.update_or_create(
                user=user,
                defaults={'consent_given': consent_given}
            )
            return Response({"message": "Consent confirmed"}, status=status.HTTP_201_CREATED)
        return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, user_id):
        try:
            user = User.objects.get(user_id=user_id)
            try:
                consent = Consent.objects.get(user=user)
                return Response({'consent_given': consent.consent_given}, status=status.HTTP_200_OK)
            except Consent.DoesNotExist:
                # Если запись согласия не найдена, возвращаем False
                return Response({'consent_given': False}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": f"User with ID {user_id} not found"}, status=status.HTTP_404_NOT_FOUND)


class SubscriptionView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        plan = request.data.get('plan')
        email = request.data.get('email')  # Email is required only during subscription purchase

        # Validate the user
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": f"User with ID {user_id} not found"}, status=status.HTTP_404_NOT_FOUND)

        # Validate the subscription plan
        if plan not in VALID_PLANS:
            return Response({"error": "Invalid plan type. Choose 'monthly' or 'yearly'."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Set subscription duration based on the plan
        if plan == "monthly":
            end_date = timezone.now() + timedelta(days=30)
        elif plan == "yearly":
            end_date = timezone.now() + timedelta(days=365)

        # Update user email only during subscription
        if email:
            user.email = email
            user.save()

        # Create or update the subscription record
        subscription, created = Subscription.objects.update_or_create(
            user=user,
            defaults={'plan': plan, 'end_date': end_date, 'is_active': True}
        )

        # Response message
        message = "Subscription created" if created else "Subscription updated"
        return Response({
            "message": message,
            "plan": plan,
            "end_date": end_date,
            "is_active": subscription.is_active
        }, status=status.HTTP_201_CREATED)


class PaymentView(APIView):
    @transaction.atomic  # Ensure atomicity for the payment operation
    def post(self, request):
        user_id = request.data.get('user_id')
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method')
        card_number = request.data.get('card_number', None)
        transaction_id = request.data.get('transaction_id', None)

        if not payment_method:
            return Response({"error": "Payment method is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(user_id=user_id)
        except ObjectDoesNotExist:
            return Response({"error": f"User with ID {user_id} not found"}, status=status.HTTP_404_NOT_FOUND)

        Payment.objects.create(
            user=user,
            amount=amount,
            payment_method=payment_method,
            card_number=card_number,
            transaction_id=transaction_id
        )
        # Update subscription statistics
        SubscriptionStatistics.objects.update_or_create(
            user=user,
            defaults={
                'total_payments': Payment.objects.filter(user=user).aggregate(total=models.Sum('amount'))['total'],
                'subscription_count': Subscription.objects.filter(user=user).count(),
                'last_payment_date': timezone.now()
            }
        )

        return Response({"message": "Payment recorded", "amount": amount}, status=status.HTTP_201_CREATED)


class UserLanguageView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(user_id=user_id)
            language = user.language if user.language else 'en'  # По умолчанию 'en'
            return Response({'language': language}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": f"User with ID {user_id} not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        user_id = request.data.get('user_id')
        language = request.data.get('language')
        if not (user_id and language):
            return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(user_id=user_id)
            user.language = language
            user.save()
            return Response({"message": "Language updated successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": f"User with ID {user_id} not found"}, status=status.HTTP_404_NOT_FOUND)


class SubscriptionView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        plan = request.data.get('plan')
        email = request.data.get('email')  # Email is required only during subscription purchase

        # Validate the user
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": f"User with ID {user_id} not found"}, status=status.HTTP_404_NOT_FOUND)

        # Validate the subscription plan
        if plan not in VALID_PLANS:
            return Response({"error": "Invalid plan type. Choose 'monthly' or 'yearly'."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Set subscription duration based on the plan
        if plan == "monthly":
            end_date = timezone.now() + timedelta(days=30)
        elif plan == "yearly":
            end_date = timezone.now() + timedelta(days=365)

        # Update user email only during subscription
        if email:
            user.email = email
            user.save()

        # Create or update the subscription record
        subscription, created = Subscription.objects.update_or_create(
            user=user,
            defaults={'plan': plan, 'end_date': end_date, 'is_active': True}
        )

        # Деактивируем старые подписки, если необходимо
        Subscription.objects.filter(user=user).exclude(id=subscription.id).update(is_active=False)

        # Response message
        message = "Subscription created" if created else "Subscription updated"
        return Response({
            "message": message,
            "plan": plan,
            "end_date": end_date,
            "is_active": subscription.is_active
        }, status=status.HTTP_201_CREATED)


class SubscriptionStatusView(APIView):
    def get(self, request, user_id):
        try:
            subscription = Subscription.objects.get(user__user_id=user_id)
            if subscription.end_date > timezone.now():
                return Response({"is_active": True, "end_date": subscription.end_date}, status=status.HTTP_200_OK)
            else:
                subscription.is_active = False
                subscription.save()
                return Response({"is_active": False, "message": "Subscription expired"}, status=status.HTTP_200_OK)
        except Subscription.DoesNotExist:
            return Response({"is_active": False, "message": "No subscription found"}, status=status.HTTP_404_NOT_FOUND)


class HelpView(APIView):
    def get(self, request):
        help_sections = HelpSection.objects.all()
        data = [{"title": section.title, "content": section.content} for section in help_sections]
        return Response(data, status=status.HTTP_200_OK)


class FeedbackView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        message = request.data.get('message')

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": f"User with ID {user_id} not found"}, status=status.HTTP_404_NOT_FOUND)

        Feedback.objects.create(user=user, message=message)
        return Response({"message": "Feedback received"}, status=status.HTTP_201_CREATED)


class PaymentCheckView(APIView):
    def post(self, request):
        payment_method = request.data.get('payment_method')
        if payment_method == 'card':
            card_number = request.data.get('card_number')
            if card_number and len(card_number) == 16:
                return Response({"message": "Card valid"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid card number"}, status=status.HTTP_400_BAD_REQUEST)
        elif payment_method == 'crypto':
            transaction_id = request.data.get('transaction_id')
            if transaction_id:
                return Response({"message": "Transaction valid"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid transaction ID"}, status=status.HTTP_400_BAD_REQUEST)


class StatisticsView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(user_id=user_id)
            stats = SubscriptionStatistics.objects.get(user=user)
            data = {
                "total_payments": stats.total_payments,
                "subscription_count": stats.subscription_count,
                "last_payment_date": stats.last_payment_date
            }
            return Response(data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": f"User with ID {user_id} not found"}, status=status.HTTP_404_NOT_FOUND)
        except SubscriptionStatistics.DoesNotExist:
            return Response({"error": "No statistics found"}, status=status.HTTP_404_NOT_FOUND)


class UserProfileView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": f"User with ID {user_id} not found"}, status=status.HTTP_404_NOT_FOUND)

        # Получаем информацию о карте
        try:
            card = UserCard.objects.get(user=user)
            card_info = {
                "card_number": card.card_number,
                "expiry_date": card.expiry_date.strftime('%m/%y')
            }
        except UserCard.DoesNotExist:
            card_info = {}

        # Получаем информацию о текущей активной подписке
        try:
            subscription = Subscription.objects.filter(user=user, is_active=True).latest('end_date')
            subscription_info = {
                "plan": subscription.plan,
                "expires_at": subscription.end_date.strftime('%Y-%m-%d')
            }
        except Subscription.DoesNotExist:
            subscription_info = {}

        data = {
            "name": user.name or "",
            "username": user.username or "",
            "card": card_info,
            "subscription": subscription_info
        }
        return Response(data, status=status.HTTP_200_OK)


class GiftSubscriptionView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        recipient_id = request.data.get('recipient_id')
        recipient_first_name = request.data.get('recipient_first_name', '')
        recipient_last_name = request.data.get('recipient_last_name', '')
        plan = request.data.get('plan')

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": f"User with ID {user_id} not found"},
                            status=status.HTTP_404_NOT_FOUND)

        # Get or create recipient user
        recipient, created = User.objects.get_or_create(
            user_id=recipient_id,
            defaults={
                'username': '',  # Since we might not have the username
                'name': f"{recipient_first_name} {recipient_last_name}".strip()
            }
        )

        plan = plan.lower()
        if plan not in VALID_PLANS:
            return Response({"error": "Invalid plan type"}, status=status.HTTP_400_BAD_REQUEST)

        end_date = calculate_subscription_end_date(plan)

        Subscription.objects.update_or_create(
            user=recipient,
            defaults={'plan': plan, 'end_date': end_date, 'is_active': True}
        )

        return Response({"message": f"Subscription gifted to {recipient.user_id}", "plan": plan},
                        status=status.HTTP_201_CREATED)


class AboutProductView(APIView):
    def get(self, request):
        product_info = {
            "name": "Premium Subscription",
            "description": "With a premium subscription, you can access all exclusive content.",
            "price_monthly": "10 USD per month",
            "price_yearly": "100 USD per year"
        }
        return Response(product_info, status=status.HTTP_200_OK)


class SupportView(APIView):
    def get(self, request):
        support_info = {
            "email": "support@example.com",
            "phone": "+123456789",
            "working_hours": "9 AM to 6 PM (Monday to Friday)"
        }
        return Response(support_info, status=status.HTTP_200_OK)


class AdviceView(APIView):
    def get(self, request):
        advice = Advice.objects.all()
        serializer = AdviceSerializer(advice, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MethodView(APIView):
    def get(self, request):
        method = Method.objects.all()
        serializer = MethodSerializer(method, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

import logging

logger = logging.getLogger(__name__)

class SaveCardView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CardSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user_id = serializer.validated_data['user_id']
                card_number = serializer.validated_data['card_number']
                expiry_date = serializer.validated_data['expiry_date']

                # Получаем пользователя
                user = User.objects.get(user_id=user_id)

                # Сохраняем или обновляем данные карты
                UserCard.objects.update_or_create(
                    user=user,
                    defaults={'card_number': card_number, 'expiry_date': expiry_date}
                )

                return Response({"message": "Card saved successfully."}, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error saving card: {e}")
                return Response({"error": "Error saving card."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.error(f"Validation error: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)