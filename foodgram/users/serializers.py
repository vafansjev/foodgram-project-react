from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Recipe
from rest_framework import serializers
from recipes.serializers import FavoriteSerializer
from users.models import User, Subscription


class UserSerializer(UserSerializer):
    """
    Сериализатор пользователя
    """
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and Subscription.objects.filter(
            user=user, author=obj).exists()


class UserCreateSerializer(UserCreateSerializer):
    """
    Сериализатор создания нового пользователя
    """
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    def validate_username(self, username):
        if len(username) < 3:
            raise serializers.ValidationError(
                'Username должен быть длиннее 3х символов'
            )
        if (not username.isalnum()) or username.isnumeric():
            raise serializers.ValidationError(
                'Username должен состоять только из букв и цифр'
            )
        return username


class SubscribeSerializer(serializers.ModelSerializer):
    """
    Сериализатор список подписок
    """
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return obj.user.is_authenticated and Subscription.objects.filter(
            user=obj.user, author=obj.author).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = Recipe.objects.filter(author=obj.author)
        limit = request.GET.get('recipes_limit')
        if limit is not None:
            recipes = recipes[:int(limit)]
        return FavoriteSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        recipes_count = Recipe.objects.filter(author=obj.author).count()
        return recipes_count
