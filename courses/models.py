from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class Instructor(models.Model):
    instructor = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    name = models.CharField(default='', max_length=200)

class Course(models.Model):
    name = models.CharField(max_length=200)
    #instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    instructor_name = models.TextField(default='')
    category = models.TextField(default='')
    description = models.TextField(default='')
    deployed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def getModules(self):
	    return Module.objects.filter(course = self)

    def addModule(self, moduleName, modulePosition):
        new_module = Module(name = moduleName, position = modulePosition, course = self)
        new_module.save()

class Module(models.Model):
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	title = models.CharField(max_length=40, default='')
	position = models.IntegerField(default=0)
	def __str__(self):
		return self.title
    
	def getComponents(self):
		return Component.objects.filter(module=self)

<<<<<<< HEAD
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

    def __str__(self):
        return self.question_text

    def get_absolute_url(self):
        return self.quiz.get_absolute_url()

class Answer(models.Model):
    # Each Question should have exactly 4 answers
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.answer_text
=======
# Component Model
class Component(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default='')
    date_of_creation = models.DateField()
    date_of_last_update = models.DateField()
    position = models.IntegerField(default=0)

    def __str__(self):
        return self.title
>>>>>>> sara-dev
