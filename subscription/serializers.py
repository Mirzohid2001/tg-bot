from rest_framework import serializers
from .models import Advice, Method, UserCard
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

    class Meta:
        model = UserCard
        fields = ['user_id', 'card_number', 'expiry_date']

    def validate_card_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Номер карты должен состоять только из цифр.")
        return value

    def validate_expiry_date(self, value):
        if not re.match(r"^(0[1-9]|1[0-2])\/\d{2}$", value):
            raise serializers.ValidationError("Срок действия должен быть в формате MM/YY.")
        return value

