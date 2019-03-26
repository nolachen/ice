from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.template import loader

from courses.forms import CourseForm, QuizForm
from courses.models import *

import logging
logger = logging.getLogger(__name__)

from django.template import loader
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test

def view_course(request,course_id):
	courseObj = Course.objects.get(id=course_id)
	x = 3
	modules = Module.objects.filter(course=courseObj).order_by("position")

	template=loader.get_template('courses/course_info.html')
	context={'course': courseObj, 'modules': modules, 'enrollStatus': x, 'participant_id': request.user.id }
	return HttpResponse(template.render(context,request))

'''def course_detail(request, course_id):
    course = Course.objects.get(id=course_id)
    return render(request, 'courses/course_detail.html', {
        'course': course,
    })'''

def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {
        'courses': courses,
    })

def loadComponents(request, course_id, module_id):
    courseObj = Course.objects.get(id=course_id)    
    moduleObj = Module.objects.get(id=module_id)
    component_list = moduleObj.getComponents().order_by("position")
    context = {'components': component_list}
    print (context)
    template = loader.get_template('courses/component_list.html')
    return HttpResponse(template.render(context,request))

"""
Responsible for adding new courses

Utilized CourseForm which is in the file forms.py
"""
def course_add(request):
    if request.POST:
        form = CourseForm(request.POST)
        if form.is_valid():
            new_course = form.save()
            return HttpResponseRedirect(new_course.get_absolute_url())
    else:
        form = CourseForm()
    return render(request, 'courses/course_form.html', {
        'form': form,
    })

def home(request):
    courses = Course.objects.all()
    return render(request, 'home.html', {
        'courses': courses,
    })

def take_quiz(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    questions=quiz.question_set.all()    
    if request.method == "POST":
        """
        To be Implemented
        form = QuizForm(request.POST, questions)
        if form.is_valid(): ## Will only ensure the option exists, not correctness.
            responses = []
            for question in questions:
                responses.append(form.cleaned_data[question])
        """
        return render(request, 'quiz/result.html', {
            
        })
    else:
        form = QuizForm(questions)
    return render(request, 'quiz/take_quiz.html', {
        "form": form,
    })
