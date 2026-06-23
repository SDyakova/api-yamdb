from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
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

    username_validator = UnicodeUsernameValidator()

    email = models.EmailField("email address", unique=True)
    bio = models.TextField("biography", blank=True)
    role = models.CharField(
        "role",
        max_length=max(len(role) for role, _ in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER,
    )
    username = models.CharField(
        "username",
        max_length=150,
        unique=True,
        validators=[username_validator],
    )

    class Meta:
        ordering = ["username"]

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR
