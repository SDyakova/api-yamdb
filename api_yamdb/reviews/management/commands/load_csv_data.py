import csv
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()
DATA_DIR = os.path.join(settings.BASE_DIR, "static", "data")

FILES = {
    "users.csv": ("users", User),
    "category.csv": ("categories", Category),
    "genre.csv": ("genres", Genre),
    "titles.csv": ("titles", Title),
    "review.csv": ("reviews", Review),
    "comments.csv": ("comments", Comment),
}


class Command(BaseCommand):
    help = "Загрузка данных из CSV-файлов"

    def handle(self, *args, **options):
        for filename, (label, model) in FILES.items():
            self.load_file(filename, label, model)
        self.load_genre_title()
        self.stdout.write(self.style.SUCCESS("Данные загружены."))

    def load_file(self, filename, label, model):
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            self.stdout.write(f"Файл {filename} не найден, пропускаем.")
            return
        with open(filepath, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.process_row(row, model)
        self.stdout.write(f"{label} загружены.")

    def process_row(self, row, model):
        if model == User:
            User.objects.get_or_create(
                id=row["id"],
                username=row["username"],
                email=row["email"],
                role=row["role"],
                bio=row["bio"],
                first_name=row["first_name"],
                last_name=row["last_name"],
            )
        elif model == Title:
            category = Category.objects.get(id=row["category"])
            Title.objects.get_or_create(
                id=row["id"],
                name=row["name"],
                year=row["year"],
                category=category,
            )
        elif model == Review:
            author = User.objects.get(id=row["author"])
            title = Title.objects.get(id=row["title_id"])
            Review.objects.get_or_create(
                id=row["id"],
                title=title,
                text=row["text"],
                author=author,
                score=row["score"],
                pub_date=row["pub_date"],
            )
        elif model == Comment:
            author = User.objects.get(id=row["author"])
            review = Review.objects.get(id=row["review_id"])
            Comment.objects.get_or_create(
                id=row["id"],
                review=review,
                text=row["text"],
                author=author,
                pub_date=row["pub_date"],
            )
        else:
            model.objects.get_or_create(**row)

    def load_genre_title(self):
        filepath = os.path.join(DATA_DIR, "genre_title.csv")
        if not os.path.exists(filepath):
            return
        with open(filepath, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = Title.objects.get(id=row["title_id"])
                genre = Genre.objects.get(id=row["genre_id"])
                title.genre.add(genre)
        self.stdout.write("Genre_title загружены.")
