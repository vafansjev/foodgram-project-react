from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from .models import Subscription, User


class CustomUserSerializer(UserSerializer):
    """
    Сериализатор пользователя
    """

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        return (
            user.is_authenticated
            and Subscription.objects.filter(user=user, author=obj).exists()
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Сериализатор создания нового пользователя
    """
    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password"
        )

    def validate_username(self, username):
        if len(username) < 3:
            raise serializers.ValidationError(
                "Username должен быть длиннее 3х символов"
            )
        if (not username.isalnum()) or username.isnumeric():
            raise serializers.ValidationError(
                "Username должен состоять только из букв и цифр"
            )
        return username
