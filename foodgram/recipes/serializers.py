from rest_framework import serializers
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from users.serializers import UserSerializer
from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
    )


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
    """Сериализатор для рецептов"""
    author = UserSerializer(read_only=True)
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
    author = UserSerializer(read_only=True)

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
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            obj = get_object_or_404(
                Ingredient,
                pk=ingredient.get('id')
            )
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=obj,
                amount=amount
            )
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


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')

# class RecipeSerializer(serializers.ModelSerializer):
#     """
#     Сериализатор рецепта
#     """
#     author = UserSerializer(read_only=True)
#     image = Base64ImageField()
#     tags = TagSerializer(many=True, read_only=True)
#     ingredients = IngredientsInRecipeSerializer(
#         many=True,
#         read_only=True,
#     )
#     is_favorited = serializers.SerializerMethodField()
#     is_in_shopping_cart = serializers.SerializerMethodField()

#     class Meta:
#         model = Recipe
#         fields = (
#             'id',
#             'tags',
#             'author',
#             'name',
#             'text',
#             'image',
#             'ingredients',
#             'cooking_time',
#             'is_favorited',
#             'is_in_shopping_cart'
#         )

#     def get_is_favorited(self, obj):
#         request = self.context.get('request')
#         return request.user.is_authenticated and (
#             Favorite.objects.filter(
#                 user=request.user, recipe=obj).exists()
#             )

#     def get_is_in_shopping_cart(self, obj):
#         request = self.context.get('request')
#         return request.user.is_authenticated and (
#             ShoppingCart.objects.filter(
#                 user=request.user, recipe=obj).exists()
#             )

#     def create(self, validated_data):
#         request = self.context.get('request')
#         ingredients = self.initial_data.get('ingredients')
#         tags = self.initial_data.get('tags')
#         recipe = Recipe.objects.create(
#             author=request.user,
#             **validated_data
#         )
#         recipe.tags.set(tags)
#         for ingredient in ingredients:
#             amount = ingredient.get('amount')
#             obj = get_object_or_404(
#                 Ingredient,
#                 pk=ingredient.get('id')
#             )
#             RecipeIngredient.objects.create(
#                 recipe=recipe,
#                 ingredient=obj,
#                 amount=amount
#             )
#         recipe.save()
#         return recipe

#     def update(self, instance, validated_data):
#         ingredients = self.initial_data.get('ingredients')
#         instance.image = validated_data.get('image', instance.image)
#         instance.name = validated_data.get('name', instance.name)
#         instance.text = validated_data.get('text', instance.text)
#         instance.cooking_time = validated_data.get(
#             'cooking_time',
#             instance.cooking_time
#         )
#         instance.tags.clear()
#         tags = self.initial_data.get('tags')
#         instance.tags.set(tags)
#         RecipeIngredient.objects.filter(recipe=instance).all().delete()
#         for ingredient in ingredients:
#             RecipeIngredient.objects.create(
#                 recipe=instance,
#                 ingredient_id=ingredient.get('id'),
#                 amount=ingredient.get('amount')
#             )
#         instance.save()
#         return instance
