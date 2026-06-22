import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class Command(BaseCommand):
    help = "Загрузка данных из CSV-файлов"

    def handle(self, *args, **options):
        data_path = os.path.join(settings.BASE_DIR, "static", "data")

        self.load_users(data_path)
        self.load_categories(data_path)
        self.load_genres(data_path)
        self.load_titles(data_path)
        self.load_reviews(data_path)
        self.load_comments(data_path)

        self.stdout.write(self.style.SUCCESS("Данные загружены."))

    def load_users(self, path):
        with open(os.path.join(path, "users.csv"), encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                User.objects.get_or_create(
                    id=row["id"],
                    username=row["username"],
                    email=row["email"],
                    role=row["role"],
                    bio=row["bio"],
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                )
        self.stdout.write("Users загружены.")

    def load_categories(self, path):
        with open(os.path.join(path, "category.csv"), encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                Category.objects.get_or_create(
                    id=row["id"],
                    name=row["name"],
                    slug=row["slug"],
                )
        self.stdout.write("Categories загружены.")

    def load_genres(self, path):
        with open(os.path.join(path, "genre.csv"), encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                Genre.objects.get_or_create(
                    id=row["id"],
                    name=row["name"],
                    slug=row["slug"],
                )
        self.stdout.write("Genres загружены.")

    def load_titles(self, path):
        with open(os.path.join(path, "titles.csv"), encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                category = Category.objects.get(id=row["category"])
                title, _ = Title.objects.get_or_create(
                    id=row["id"],
                    name=row["name"],
                    year=row["year"],
                    category=category,
                )
        self.stdout.write("Titles загружены.")

    def load_genre_title(self, path):
        with open(
            os.path.join(path, "genre_title.csv"), encoding="utf-8"
        ) as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = Title.objects.get(id=row["title_id"])
                genre = Genre.objects.get(id=row["genre_id"])
                title.genre.add(genre)
        self.stdout.write("Genre_title загружены.")

    def load_reviews(self, path):
        with open(os.path.join(path, "review.csv"), encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
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
        self.stdout.write("Reviews загружены.")

    def load_comments(self, path):
        with open(os.path.join(path, "comments.csv"), encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                author = User.objects.get(id=row["author"])
                review = Review.objects.get(id=row["review_id"])
                Comment.objects.get_or_create(
                    id=row["id"],
                    review=review,
                    text=row["text"],
                    author=author,
                    pub_date=row["pub_date"],
                )
        self.stdout.write("Comments загружены.")
