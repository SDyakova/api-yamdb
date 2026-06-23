from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ("name", "year", "category", "genre_list")
    list_editable = ("category",)
    search_fields = ("name",)
    list_filter = ("category", "genre")

    def genre_list(self, obj):
        return ", ".join(g.name for g in obj.genre.all())

    genre_list.short_description = "Жанры"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "title", "score", "pub_date")
    search_fields = ("text", "author__username")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "review", "pub_date")
    search_fields = ("text", "author__username")
