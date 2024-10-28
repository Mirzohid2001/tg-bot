from django.db import models


class User(models.Model):
    user_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255,null=True, blank=True)
    username = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    registration_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Consent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    consent_given = models.BooleanField(default=False)
    consent_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=100)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    card_number = models.CharField(max_length=16, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class HelpSection(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return self.title


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class SubscriptionStatistics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_payments = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    subscription_count = models.IntegerField(default=0)
    last_payment_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username
