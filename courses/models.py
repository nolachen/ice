from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models

# Create your models here.
class Course(models.Model):
    # Define the attributes to be stored

    # A course name with maximum of 200 characters
    name = models.CharField(max_length=200)
    description = models.TextField(default='')
    deployed = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('course_detail', args=(self.id, ))

class Instructor(models.Model):
    instructor = models.OneToOneField(
        User,
        primary_key=True,
        on_delete=models.PROTECT
    )

# Component Model
class Component(models.Component):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    date_of_creation = models.DateField()
    date_of_last_update = models.DateField()
    index = models.IndexField()

    class Meta:
        astract = True
        ordering = ['index']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.index:
            self.index = self.module.components.count() - 1
        super(Component, self).save(*args, **kwargs)

class TextComponent(Component):
    text_passage = models.CharField(max_length=200)

class ImageComponent(Component):
    image_details = models.CharField(max_length=200)