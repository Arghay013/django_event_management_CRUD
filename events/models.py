from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="events")
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="events_participating_in",
    )

    def __str__(self):
        return self.name