from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith')

    class Meta:
        fields = ('name', )
        model = Ingredient


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )
    tag = filters.AllValuesMultipleFilter(field_name='tag__slug')

    class Meta:
        fields = ('tag', 'author', 'is_favorited', 'is_in_shopping_cart', )
        model = Recipe

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(fav_recipes__user=user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(shopping_cart__user=user)
        return queryset
