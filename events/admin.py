from django.contrib import admin
from .models import Event, Category, UserProfile

# Register your models here.
admin.site.register(Event)
admin.site.register(Category)
admin.site.register(UserProfile)
