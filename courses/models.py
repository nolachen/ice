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