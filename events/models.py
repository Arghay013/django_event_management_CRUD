from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import os


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
    image = models.ImageField(upload_to='events/', default='events/default_event.jpg', blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="events")
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="events_participating_in",
    )

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """Extended user profile with additional information and phone number validation"""

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message='Phone number must be entered in the format: +1234567890. Up to 15 digits allowed.',
        code='invalid_phone'
    )
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    
    profile_picture = models.ImageField(
        upload_to='profiles/',
        default='profiles/default_profile.jpg',
        blank=True,
        null=True,
        help_text='Upload a profile picture (JPG, PNG, GIF)'
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        help_text='Enter phone number with country code (e.g., +8801*********)'
    )
    
    bio = models.TextField(blank=True, null=True, help_text='Tell us about yourself')
    date_of_birth = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}'s Profile"
    
    def get_profile_picture_url(self):
        """Get profile picture URL or return default"""
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/images/default_profile.jpg'
    
    def is_phone_valid(self):
        """Check if phone number is valid"""
        if not self.phone_number:
            return True
        try:
            self.full_clean()
            return True
        except:
            return False