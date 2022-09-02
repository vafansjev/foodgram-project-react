from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from users.models import Subscription
from users.serializers import CustomUserSerializer

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор тегов
    """
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингридиентов
    """
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингридиентов в рецепте
    """
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeViewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для рецептов
    """
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientsInRecipeSerializer(
        many=True,
        read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = request.user
        return (
            user.is_authenticated
            and Favorite.objects.filter(
                user=user,
                recipe=obj,
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        user = request.user
        return (
            user.is_authenticated
            and ShoppingCart.objects.filter(
                user=user,
                recipe=obj,
            ).exists()
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов"""
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    ingredients = IngredientsInRecipeSerializer(
        many=True,
        read_only=True)
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        recipe = Recipe.objects.create(
            author=request.user,
            **validated_data
        )
        recipe.tags.set(tags)
        ingredient_objects = []
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            instance = get_object_or_404(
                Ingredient,
                pk=ingredient.get('id')
            )
            ingredient_objects.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=instance,
                    amount=amount
                )
            )
        RecipeIngredient.objects.bulk_create(ingredient_objects)
        return recipe

    def update(self, instance, validated_data):
        ingredients = self.initial_data.get('ingredients')
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.tags.clear()
        tags = self.initial_data.get('tags')
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).all().delete()
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
        return instance


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода избранных рецептов
    """
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления в избранное
    """
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    """
    Сериализатор список подписок
    """

    email = serializers.ReadOnlyField(source="author.email")
    id = serializers.ReadOnlyField(source="author.id")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        return Subscription.objects.filter(
            user=obj.user, author=obj.author).exists()

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes = Recipe.objects.filter(author=obj.author)
        limit = request.GET.get("recipes_limit")
        if limit is not None:
            recipes = recipes[: int(limit)]
        return FavoriteRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(
                author=obj.author).count()
