from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    description = models.CharField('Description', max_length=100)
    profile_picture = models.ImageField('Profile picture',
        upload_to='profiles/',
        default='profiles/placeholder.png'
    )
    def __str__(self):
        return self.user.username

    def username(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse("profiles:profile_page", kwargs={"username": self.username()})
