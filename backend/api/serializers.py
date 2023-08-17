from rest_framework import serializers

from recipes.models import Tag, Ingredient


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'color', 'slug',)
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'measurement_unit',)
        model = Ingredient
