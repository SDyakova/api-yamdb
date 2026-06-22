from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    ROLE_CHOICES = [
        (USER, "User"),
        (MODERATOR, "Moderator"),
        (ADMIN, "Admin"),
    ]

    email = models.EmailField("email address", unique=True)
    bio = models.TextField("biography", blank=True)
    role = models.CharField(
        "role", max_length=20, choices=ROLE_CHOICES, default=USER
    )

    class Meta:
        ordering = ["id"]

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR
