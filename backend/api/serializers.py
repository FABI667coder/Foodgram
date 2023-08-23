from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (FavoriteRecipe, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)
from users.models import Subscribe, User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        model = User

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=request.user, author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'color', 'slug',)
        read_only_fields = fields
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit', )
        read_only_fields = fields
        model = Ingredient


class IngredientRecipeWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        fields = ('id', 'amount', )
        model = IngredientRecipe


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount', )
        model = IngredientRecipe


class RecipeReadSerializer(serializers.ModelSerializer):
    tag = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredient = IngredientRecipeSerializer(
        many=True,
        read_only=True,
        source='ingredient_recipes'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        fields = (
            'id',
            'tag',
            'author',
            'ingredient',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = fields
        model = Recipe

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=request.user, recipe=obj).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredient = IngredientRecipeWriteSerializer(many=True)
    tag = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    author = UserSerializer(read_only=True)
    image = Base64ImageField

    class Meta:
        model = Recipe
        fields = (
            'ingredient',
            'author',
            'tag',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def connect_ingredient_tag(self, recipe, ingredient, tag):
        for _tag in tag:
            recipe.tag.add('_tag')
            recipe.save()
        for _ingredient in ingredient:
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )

    def create(self, validated_data):
        ingredient = validated_data.pop('ingredient')
        tag = validated_data.pop('tag')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        self.connect_ingredient_tag(
            recipe=recipe, ingredient=ingredient, tag=tag,
        )
        return recipe

    def update(self, instance, validated_data):
        ingredient = validated_data.pop('ingredient')
        tag = validated_data.pop('tag')
        instance.ingredients.clear()
        instance.tag.clear()
        self.connect_ingredient_tag(
            recipe=instance, ingredients=ingredient, tag=tag,
        )
        return super().update(instance, validated_data)


class RecipeSubscriberSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_fields = fields
        model = Recipe


class SubscribeSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        model = User

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=request.user, author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipe = obj.recipes.all()
        limit = request.GET.get('recipes_limit')
        if limit:
            recipe = recipe[:int(limit)]
        return RecipeSubscriberSerializer(recipe, many=True).data


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time', )
        model = FavoriteRecipe


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time',)
        model = ShoppingCart