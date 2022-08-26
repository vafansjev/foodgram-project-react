from django.db import models
from colorfield.fields import ColorField
from users.models import User
from django.core.validators import MinValueValidator


class Tag(models.Model):
    """
    Модель для хранения тэгов
    """
    COLOR_PALETTE = [
        ('#FFFFFF', 'white', ),
        ('#000000', 'black', ),
        ('#F51302', 'red'),
        ('#FAAC02', 'orange'),
        ('#FFFB03', 'yellow'),
        ('#28FF03', 'green'),
        ('#03FcF0', 'cyan'),
        ('#030BFF', 'blue'),
        ('#FC03F4', 'purple')
    ]

    name = models.CharField(
        unique=True,
        max_length=50,
        verbose_name='Название тега рецепта'
    )
    color = ColorField(
        samples=COLOR_PALETTE,
        verbose_name='hex цвета тэга'
    )
    slug = models.SlugField(
        max_length=10,
        unique=True,
        verbose_name='Поле slug для цвета'
    )

    class Meta:
        ordering = ['slug']
        verbose_name = 'Тэг'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Модель ингридиентов
    """
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name='Название ингридиента'
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Единицы измерения'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингридиент'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        verbose_name='Картинка рецепта',
        upload_to='recipes/images/'
    )
    text = models.TextField(
        verbose_name='Текст рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время готовки в минутах',
        validators=[
            MinValueValidator(
                1, message='Время приготовления минимум 1 минута!'
            )
        ],
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """
    Модель для количества ингридиентов в рецепте
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингридиент',
        related_name='+'
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Количество ингридиента',
        validators=[
            MinValueValidator
            (
                1, message='Должен быть минимум 1 ингридиент!'
            )
        ],
    )

    class Meta:
        verbose_name = 'Ингриденты в рецепте'
        ordering = ['-id']
        constraints = (
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingridients'
            ),
        )

    def __str__(self):
        return f'{self.recipe}, {self.ingredient}'


class Favorite(models.Model):
    """
    Модель избранных рецептов
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorites'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        constraints = (
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorites'
            ),
        )

    def __str__(self):
        return f'{self.recipe}, {self.user}'


class ShoppingCart(models.Model):
    """
    Корзина для покупок
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Продуктовая корзина'
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_shopping_cart'
            ),
        )

    def __str__(self):
        return f'{self.user}, {self.recipe}'
