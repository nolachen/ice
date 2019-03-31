from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models
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
        new_module = Module(name = moduleName, index = modulePosition, course = self)
        new_module.save()

    def get_absolute_url(self):
        return reverse('course_detail', args=(self.id, ))

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
    #is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    correct_answer = models.ForeignKey(Choice, on_delete=models.CASCADE, default=0)

class QuizResult(models.Model):
    quiz = models.ForeignKey(Module, on_delete=models.CASCADE)
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE)
    result = models.CharField(max_length=20)
    passed = models.BooleanField(default=False)

    def record_passed_quiz(quiz_id, learner_id):
        new_result = QuizResult(quiz_id=quiz_id, learner_id=learner_id, passed=True)
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
        abstract = True
        ordering = ['index']

    def __str__(self):
        return self.title

class TextComponent(Component):
    text_passage = models.TextField()

class ImageComponent(Component):
    image_details = models.CharField(max_length=200)