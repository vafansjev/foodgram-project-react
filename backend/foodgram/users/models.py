from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint


class User(AbstractUser):
    """
    Модель пользователя
    """
    email = models.EmailField(
        db_index=True,
        unique=True,
        max_length=150,
        verbose_name='Email-адрес'
    )

    username = models.CharField(
        db_index=True,
        unique=True,
        max_length=100,
        verbose_name='Псевдоним пользователя'
    )

    first_name = models.CharField(
        max_length=100,
        verbose_name='Имя пользователя'
    )

    last_name = models.CharField(
        max_length=100,
        verbose_name='Фамилия пользователя'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    class Meta:
        verbose_name = 'Пользователь'
        ordering = ['-id']
        constraints = (
            UniqueConstraint(
                fields=('email', 'username'),
                name='unique_username'
            ),
        )

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """
    Модель подписки
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка на автора',
        constraints = (
            UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow'
            ),
        )

    def __str__(self):
        return self.user.username
