from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


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

class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    # index of ordering within the course
    index = models.IntegerField()

    class Meta:
        ordering = ['index']

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.index:
            # Default the index to the last one in the sequence
            self.index = self.course.modules.count() - 1
        super(Module, self).save(*args, **kwargs)

class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    # Optional; If a module is deleted, just set the module for this quiz to null
    module = models.OneToOneField(Module, on_delete=models.SET_NULL, null=True, blank=True)

    num_questions = models.IntegerField()
    passing_score = models.FloatField(validators=[MaxValueValidator(100), MinValueValidator(0)])

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_text = models.TextField()

class Answer(models.Model):
    # Each Question should have exactly 4 answers
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()
    is_correct = models.BooleanField()

    def __str__(self):
        return self.answer_text

# Component Model
class Component(models.Model):
    course = models.ForeignKey(Course, related_name="components", on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    date_of_creation = models.DateField()
    date_of_last_update = models.DateField()
    index = models.IntegerField()

    class Meta:
        abstract = True
        ordering = ['index']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.index:
            self.index = self.course.components.count() - 1
        super(Component, self).save(*args, **kwargs)

class TextComponent(Component):
    text_passage = models.TextField()

class ImageComponent(Component):
    image_details = models.CharField(max_length=200)