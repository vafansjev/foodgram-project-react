from django.http import HttpResponse
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .filters import IngredientSearchFilter, RecipeFilter
from .permissions import IsAuthorOrAdminOrReadOnly
from .pagination import PageNumberPagination

from .models import (
    ShoppingCart,
    Tag,
    Ingredient,
    Recipe,
    Favorite,
    RecipeIngredient)
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    FavoriteSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = None
    filterset_class = IngredientSearchFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_class = RecipeFilter

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='favorite',
        permission_classes=[IsAuthenticated],
        serializer_class=FavoriteSerializer
    )
    def favorite(self, request, pk=id):
        user = request.user
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            favorite = Favorite.objects.create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(favorite)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        favorite = get_object_or_404(Favorite, user=user, recipe__id=pk)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated],
        serializer_class=FavoriteSerializer
    )
    def shopping_cart(self, request, pk=id):
        user = request.user
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            favorite = ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(favorite)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        favorite = get_object_or_404(ShoppingCart, user=user, recipe__id=pk)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        cart = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user).values(
                'ingredient__name', 'ingredient__measurement_unit').annotate(
                    amount=Sum('amount')
                )
        text = 'Купить ингридиенты (продукты): \n'
        for ingredient in cart:
            name = ingredient['ingredient__name']
            amount = ingredient['amount']
            measure = ingredient['ingredient__measurement_unit']

            text += (f'{name}: {amount}, {measure}\n')

        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shoplist.txt"'
        return response
