from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .constants import (
    MAX_LENGTH_NAME,
    MAX_LENGTH_SLUG,
    MAX_SCORE,
    MIN_SCORE,
    TEXT_LIMIT,
)

User = get_user_model()


class NameSlugBase(models.Model):
    name = models.CharField("Название", max_length=MAX_LENGTH_NAME)
    slug = models.SlugField("Слаг", unique=True, max_length=MAX_LENGTH_SLUG)

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(NameSlugBase):
    class Meta(NameSlugBase.Meta):
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Genre(NameSlugBase):
    class Meta(NameSlugBase.Meta):
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"


class Title(models.Model):
    name = models.CharField("Название", max_length=MAX_LENGTH_NAME)
    year = models.PositiveSmallIntegerField("Год выпуска")
    description = models.TextField("Описание", blank=True)
    genre = models.ManyToManyField(
        Genre, related_name="titles", verbose_name="Жанр"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="titles",
        null=True,
        blank=True,
        verbose_name="Категория",
    )

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"

    def __str__(self):
        return self.name


class ReviewCommentBase(models.Model):
    text = models.TextField("Текст")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Автор"
    )
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ["-pub_date"]

    def __str__(self):
        return f"{self.author.username}: {self.text[:TEXT_LIMIT]}"


class Review(ReviewCommentBase):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Произведение",
    )
    score = models.PositiveSmallIntegerField(
        "Оценка",
        validators=[
            MinValueValidator(MIN_SCORE),
            MaxValueValidator(MAX_SCORE),
        ],
    )

    class Meta(ReviewCommentBase.Meta):
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        constraints = [
            models.UniqueConstraint(
                fields=["title", "author"], name="unique_review"
            )
        ]


class Comment(ReviewCommentBase):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Отзыв",
    )

    class Meta(ReviewCommentBase.Meta):
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
