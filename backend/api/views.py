from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, response, status, viewsets
from rest_framework.decorators import action

from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            Tag)
from users.models import Subscribe, User
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsOwnerOrReadOnly
from .serializers import (FavoriteRecipeSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          ShoppingCartSerializer, SubscribeSerializer,
                          TagSerializer)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all().order_by('id')
    permission_classes = [permissions.AllowAny]

    @action(
        detail=False,
        methods=['GET'],
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(author__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages, many=True, context={'request': request},
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
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return response.Response(
                {'errors': 'Вы не можете подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        is_subscribe = Subscribe.objects.filter(
            user=user, author=author
        ).exists()
        if request.method == 'POST':
            if is_subscribe:
                return response.Response(
                    {'errors': 'Вы уже подписаны на данного автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscribe.objects.create(
                user=user,
                author=author
            )
            serializer = SubscribeSerializer(
                author,
                context={'request': request}
            )
            return response.Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
        else:
            if not is_subscribe:
                return response.Response(
                    {'errors': 'Вы не подписаны на данного автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscribe.objects.filter(user=request.user, author=author).delete()
            return response.Response(
                status=status.HTTP_204_NO_CONTENT,
            )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
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
        is_favorited = FavoriteRecipe.objects.filter(
            user=user, recipe=recipe
        ).exists()
        if request.method == 'POST':
            if is_favorited:
                return response.Response(
                    {'errors': 'Вы уже добавили данный рецепт в избранное'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = FavoriteRecipeSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(recipe=recipe, user=user)
            return response.Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if not is_favorited:
            return response.Response(
                {'errors': 'Данного рецепта нет в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        FavoriteRecipe.objects.filter(
            recipe=recipe, user=user
        ).delete()
        return response.Response(
            status=status.HTTP_204_NO_CONTENT,
        )

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
        is_in_shopping_cart = ShoppingCart.objects.filter(
            user=user, recipe=recipe
        ).exists()
        if request.method == 'POST':
            if is_in_shopping_cart:
                return response.Response(
                    {'errors': 'Вы уже добавили данный рецепт в список'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = ShoppingCartSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(recipe=recipe, user=user, )
            return response.Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        if not is_in_shopping_cart:
            return response.Response(
                {'errors': 'Данного рецепта нет в списке'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingCart.objects.filter(
            recipe=recipe, user=user
        ).delete()
        return response.Response(
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
    )
    def create_shopping_cart_list(self, request):
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user)
        ingredients = {}
        for cart_item in shopping_cart:
            recipe = cart_item.recipe
            for ingredient_recipe in recipe.ingredient_recipes.all():
                ingredient = ingredient_recipe.ingredient
                amount = ingredient_recipe.amount
                if ingredient in ingredients:
                    ingredients[ingredient] += amount
                else:
                    ingredients[ingredient] = amount
        content = []
        for ingredient, amount in ingredients.items():
            content.append(
                f'{ingredient.name} - {amount} '
                f'{ingredient.measurement_unit}'
            )
        content = '\n'.join(content)
        response = HttpResponse(
            content, content_type='text/plain'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response
