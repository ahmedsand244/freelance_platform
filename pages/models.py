from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Service Category'
        verbose_name_plural = 'Service Categories'

    def __str__(self):
        return self.name


class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            self.compress_image()

    def compress_image(self):
        img = Image.open(self.image.path)
        img = img.convert('RGB')
        img.thumbnail((800, 800))
        img.save(self.image.path, format='WEBP', quality=85)

    def __str__(self):
        return self.title


class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=200)
    image = models.ImageField(upload_to='team/')
    facebook_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            self.compress_image()

    def compress_image(self):
        img = Image.open(self.image.path)
        img = img.convert('RGB')
        img.thumbnail((800, 800))
        img.save(self.image.path, format='WEBP', quality=85)

    def __str__(self):
        return self.name


class Partner(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='partners/')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.logo:
            self.compress_logo()

    def compress_logo(self):
        img = Image.open(self.logo.path)

        if img.mode in ("RGBA", "LA"):  # لو فيها شفافية
            img = img.convert("RGBA")
            img.thumbnail((800, 800))
            img.save(self.logo.path, format='PNG')
        else:
            img = img.convert("RGB")
            img.thumbnail((800, 800))
            img.save(self.logo.path, format='WEBP', quality=85)

    def __str__(self):
        return self.name