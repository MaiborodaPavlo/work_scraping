from django.db import models

from .utils import slug_cir_to_en


class City(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.CharField(max_length=50, blank=True, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_cir_to_en(str(self.name))
        super().save()


class Language(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.CharField(max_length=50, blank=True, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_cir_to_en(str(self.name))
        super().save()


class Vacancy(models.Model):
    url = models.URLField(unique=True)
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    description = models.TextField()
    city = models.ForeignKey('City', on_delete=models.CASCADE)
    language = models.ForeignKey('Language', on_delete=models.CASCADE)
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title
