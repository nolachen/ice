from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models

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

# Component Model
class Component(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default='')
    date_of_creation = models.DateField()
    date_of_last_update = models.DateField()
    position = models.IntegerField(default=0)

    def __str__(self):
        return self.title
