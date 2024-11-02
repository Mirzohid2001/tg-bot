from rest_framework import serializers
from .models import Advice, Method, UserCard
from datetime import date

import re


class AdviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advice
        fields = ('id', 'title', 'content')


class MethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Method
        fields = ('id', 'title', 'content')

class CardSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    card_number = serializers.CharField(max_length=16)
    expiration_date = serializers.DateField(input_formats=['%m/%y', '%m-%Y'])
    print(f"Expiry date being sent to backend: {expiration_date}")

    expiration_date = serializers.DateField(
        input_formats=['%m/%y', '%m-%Y', '%m/%Y'],  # Added '%m/%Y'
        error_messages={
            'invalid': 'Date has wrong format. Use one of these formats instead: MM/YY, MM-YYYY, MM/YYYY.'
        }
    )


    class Meta:
        model = UserCard
        fields = ['user_id', 'card_number', 'expiration_date']

    def validate_card_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Номер карты должен состоять только из цифр.")
        if len(value) != 16:
            raise serializers.ValidationError("Длина номера карты должна быть 16 цифр.")
        return value

    def validate_expiry_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("Срок действия карты истёк.")
        return value