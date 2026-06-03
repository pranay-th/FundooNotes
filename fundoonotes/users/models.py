from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email        = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    is_verified  = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["username", "phone_number"]

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.username
