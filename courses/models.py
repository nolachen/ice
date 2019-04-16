from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models
from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator

class Learner(models.Model):
    learner = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

class Instructor(models.Model):
    instructor = models.OneToOneField(
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
    #instructor_name = models.TextField(default='')
    cecu_value = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(default='')
    deployed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def getModules(self):
	    return Module.objects.filter(course = self)

    def addModule(self, moduleName, modulePosition):
        new_module = Module(name = moduleName, index = modulePosition, course = self)
        new_module.save()

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
            # Default the index to the last one in the sequence
            self.index = self.course.modules.count() - 1
        super(Module, self).save(*args, **kwargs)
    
    def getComponents(self):
        return TextComponent.objects.filter(module=self)

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, related_name="quizzes", on_delete=models.CASCADE)
    # Optional; If a module is deleted, just set the module for this quiz to null
    module = models.OneToOneField(Module, on_delete=models.SET_NULL, null=True, blank=True)

    num_questions = models.IntegerField()
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
    quiz = models.ForeignKey(Module, on_delete=models.CASCADE)
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE)
    # Result will be stored in the form of over a hundred
    # For example, if a learner score 4 out of 5 questions, the result stored will be 80.0
    result = models.FloatField(validators=[MaxValueValidator(100), MinValueValidator(0)])
    passed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

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
    index = models.IntegerField()

    class Meta:
        ordering = ['index']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.index:
            # Default the index to the last one in the sequence
            self.index = self.course.components.count() - 1
        super(Component, self).save(*args, **kwargs)

class TextComponent(Component):
    text_passage = models.TextField()

class ImageComponent(Component):
    image_details = models.CharField(max_length=200)
    image = models.ImageField(default=None, blank=True, null=True, upload_to='images/')

class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)

    def enrol(learner, course):
        new_enrollment = Enrollment(learner=learner, course=course)
        new_enrollment.save()

    def update_date(self, date):
        self.completed_date = date 
        self.save()
