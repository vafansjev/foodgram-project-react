from django_filters import rest_framework as filter
from recipes.models import Ingredient, Recipe


class IngredientSearchFilter(filter.FilterSet):
    name = filter.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class RecipeFilter(filter.FilterSet):
    tags = filter.CharFilter(
        field_name='tags__slug',
        method='filter_tags'
    )
    is_favorited = filter.CharFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = filter.CharFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def filter_tags(self, queryset, slug, tags):
        tags = self.request.query_params.getlist('tags')
        return queryset.filter(tags__slug__in=tags).distinct()

    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
