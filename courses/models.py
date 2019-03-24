from django.urls import reverse
from django.db import models

# Create your models here.
class Course(models.Model):
    # Define the attributes to be stored

    # A course name with maximum of 200 characters
    name = models.CharField(max_length=200)

    def get_absolute_url(self):
        return reverse('course_detail', args=(self.id, ))


# Component Model
class Component(models.Component):
    title = models.CharField(max_length=200)
    date_of_creation = models.DateField()
    date_of_last_update = models.DateField()
    index = models.IndexField()
