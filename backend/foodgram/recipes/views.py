from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientSearchFilter, RecipeFilter
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)
from .pagination import PageNumberPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, RecipeViewSerializer,
                          TagSerializer)

GET_METHOD = 'GET'
POST_METHOD = 'POST'
DELETE_METHOD = 'DELETE'


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
    serializer_class = RecipeViewSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == GET_METHOD:
            return RecipeViewSerializer
        return RecipeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        return serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        serializer = RecipeViewSerializer(
            instance=serializer.instance,
            context={'request': self.request},
        )
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )

    @action(
        methods=[POST_METHOD, DELETE_METHOD],
        detail=True,
        url_path='favorite',
        permission_classes=[IsAuthenticated],
        serializer_class=FavoriteSerializer
    )
    def favorite(self, request, pk=id):
        user = request.user
        if request.method == POST_METHOD:
            recipe = get_object_or_404(Recipe, pk=pk)
            favorite = Favorite.objects.create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(favorite)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        favorite = get_object_or_404(Favorite, user=user, recipe__id=pk)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=[POST_METHOD, DELETE_METHOD],
        detail=True,
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated],
        serializer_class=FavoriteSerializer
    )
    def shopping_cart(self, request, pk=id):
        user = request.user
        if request.method == POST_METHOD:
            recipe = get_object_or_404(Recipe, pk=pk)
            favorite = ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(favorite)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        favorite = get_object_or_404(ShoppingCart, user=user, recipe__id=pk)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=[GET_METHOD],
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        cart = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user).values_list(
            'ingredient__name', 'ingredient__measurement_unit').order_by(
                'ingredient__name').annotate(ingredient_total=Sum('amount'))
        text = 'Купить ингридиенты (продукты): \n'
        for ingredients in cart:
            name, measurement_unit, amount = ingredients
            text += f'{name}: {amount} {measurement_unit}\n'
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping-list.txt"'
        )
        return response
