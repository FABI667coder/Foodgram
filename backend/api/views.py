from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, response, status, viewsets
from rest_framework.decorators import action

from recipes.models import (FavoriteRecipe, Ingredient,
                            Recipe, ShoppingCart, Tag)
from users.models import Subscribe, User
from .filters import IngredientFilter, RecipeFilter
from .pagination import PagePagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (FavoriteRecipeSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          ShoppingCartSerializer, SubscribeSerializer,
                          TagSerializer)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = PagePagination

    @action(
        detail=False,
        methods=['GET'],
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscriptions(self, request):
        user = request.user
        queryset = user.subscriber.all()
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='subscribe',
        url_name='subscribe',
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                author,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=request.user, author=author)
            return response.Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        elif request.method == 'DELETE':
            Subscribe.objects.filter(user=request.user, author=author).delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='favorite',
        url_name='favorite',
    )
    def favorite_recipe(self, request, pk=None):
        recipe = get_object_or_404(
            Recipe, id=pk
        )
        user = request.user
        if request.method == 'POST':
            serializer = FavoriteRecipeSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(recipe=recipe, user=user)
            return response.Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        elif request.method == 'DELETE':
            FavoriteRecipe.objects.filter(
                recipe=recipe, user=user
            ).delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        return response.Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='shopping_cart',
        url_name='shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(
            Recipe, id=pk
        )
        user = request.user
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(recipe=recipe, user=user,)
            return response.Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        elif request.method == 'DELETE':
            ShoppingCart.objects.filter(
                recipe=recipe, user=user
            ).delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        return response.Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='download_shopping_cart'
    )
    def create_shopping_cart_list(self, request):
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user)
        ingredients = []
        for cart_item in shopping_cart:
            recipe = cart_item.recipe
            for ingredient_recipe in recipe.ingredient_recipes.all():
                ingredient = ingredient_recipe.ingredient
                amount = ingredient_recipe.amount
                ingredients.append(
                    f'{ingredient.name} - '
                    f'{amount} {ingredient.measurement_unit}'
                )
        content = '\n'.join(ingredients)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response
