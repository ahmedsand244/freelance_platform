from django.contrib.auth.models import AbstractUser
from django.db import models

from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    is_organizer = models.BooleanField(default=False)
    is_client = models.BooleanField(default=True)  
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.username
