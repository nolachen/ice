from django.shortcuts import render
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.template import loader

from courses.forms import CourseForm
from courses.models import Course, Module, Component

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

	template=loader.get_template('courseInfo.html')
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
    template = loader.get_template('componentList.html')
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