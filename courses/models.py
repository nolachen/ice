from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models
from django import forms
from django.utils.html import format_html
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator

class Learner(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    staff_id = models.CharField(max_length=8, validators=[MinLengthValidator(8)], unique=True)
    cecu_awarded = models.PositiveSmallIntegerField()

    def award_cecu_credit(self, cecu_value):
        self.cecu_awarded += cecu_value

class Instructor(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    autobiography = models.TextField(default='')

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=200)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    cecu_value = models.PositiveSmallIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(default='')
    deployed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("courses:view_course", args={self.id})

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
            # Default the index to the last one in the course
            self.index = Module.objects.filter(course=self.course).count()
        super(Module, self).save(*args, **kwargs)
    
    def add_component(self, component, index=None):
        component.module = self
        if index:
            component.index = index
        component.save()

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, related_name="quizzes", on_delete=models.CASCADE)
    # Optional; If a module is deleted, just set the module for this quiz to null
    module = models.OneToOneField(Module, on_delete=models.SET_NULL, null=True, blank=True)

    num_questions = models.PositiveSmallIntegerField()
    passing_score = models.FloatField(validators=[MaxValueValidator(100), MinValueValidator(0)])

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_text = models.TextField()

    def __str__(self):
        return self.question_text

    def get_absolute_url(self):
        return self.quiz.get_absolute_url()

class Choice(models.Model):
    # Each Question should have exactly 4 choices
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.TextField()

    def __str__(self):
        return self.choice_text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    correct_answer = models.ForeignKey(Choice, on_delete=models.CASCADE, default=0)

class QuizResult(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE)
    # Result will be stored in the form of over a hundred
    # For example, if a learner score 4 out of 5 questions, the result stored will be 80.0
    result = models.FloatField(validators=[MaxValueValidator(100), MinValueValidator(0)])
    passed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def new_record(quiz_id, learner, result, passed):
        new_result = QuizResult(quiz_id=quiz_id, learner=learner, result=result, passed=passed)
        new_result.save()

# Component Model
class Component(models.Model):
    course = models.ForeignKey(Course, related_name="%(class)ss", on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.SET_NULL, null=True, blank=True)

    title = models.CharField(max_length=200)
    date_of_creation = models.DateField(auto_now_add=True)
    date_of_last_update = models.DateField(auto_now=True)

    # Order within the module
    index = models.IntegerField(null=True, blank=True)

    TEXT = 'TX'
    IMAGE = 'IM'
    COMPONENT_TYPES = (
        (TEXT, 'Text'),
        (IMAGE, 'Image')
    )
    # Store the child component type so we can access it
    component_type = models.CharField(max_length=2, choices=COMPONENT_TYPES)

    class Meta:
        ordering = ['index']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Only set an index if the component belongs to a module
        if self.index is None and self.module:
            # Default the index to the last one in the sequence
            self.index = Component.objects.filter(module=self.module).count()
        # If we remove a component from its module, reset the index
        if self.index is not None and not self.module:
            self.index = None
        super(Component, self).save(*args, **kwargs)

    def get_child_component(self):
        if self.component_type == Component.TEXT:
            return self.textcomponent
        elif self.component_type == Component.IMAGE:
            return self.imagecomponent
        else:
            raise TypeError
    
    def get_html_representation(self):
        raise NotImplementedError

# Note: all subclasses of Component MUST have override get_html_representation method
class TextComponent(Component):
    text_passage = models.TextField()

    def get_html_representation(self):
        return format_html("<p class=\"card-text\">{}</p>", self.text_passage)

class ImageComponent(Component):
    image_details = models.TextField()
    image = models.ImageField(upload_to='images/')

    def get_html_representation(self):
        return format_html("<div><img src={} class=\"pb-2\"/><p class=\"card-text\">{}</p></div>", self.image.url, self.image_details)

class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)

    @staticmethod
    def enroll(learner, course):
        new_enrollment = Enrollment(learner=learner, course=course)
        new_enrollment.save()
