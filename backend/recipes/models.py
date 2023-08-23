from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=settings.MAX_VAL200,
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=settings.MAX_VAL200,
    )

    class Meta:
        verbose_name = 'Ингредиенты'
        verbose_name_plural = 'Ингредиенты'


class Tag(models.Model):
    name = models.CharField(
        'Название',
        unique=True,
        max_length=settings.MAX_VAL150,
    )
    color = models.CharField(
        'Цвет',
        unique=True,
        max_length=7,
    )
    slug = models.SlugField(
        unique=True,
        max_length=settings.MAX_VAL150,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Тег'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        related_name='recipes',
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        'Название',
        max_length=settings.MAX_VAL200,
    )
    text = models.TextField(
        'Описание',
    )
    image = models.ImageField(
        upload_to='app/',
        null=True,
    )
    ingredient = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    tag = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(
                settings.MIN_SCORE,
                message='Минимальное время приготовления 1 минута'
            ),
        ]
    )

    pub_date = models.DateTimeField(
        'Время публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'Рецепты'
        verbose_name_plural = 'Рецепты'


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='ingredient_recipes',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        related_name='ingredient_recipes',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=(
            MinValueValidator(
                settings.MIN_SCORE,
                message='Выберите хотя бы 1 ингредиент'
            ),
        ),
    )

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='fav_recipes',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='fav_recipes',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранный рецепт'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='shopping_cart',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='shopping_cart',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
