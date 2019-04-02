from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse

from courses.forms import CourseForm, ModuleForm, QuizForm
from courses.models import Instructor, Course, Module, Quiz, Learner, Enrolment

import logging
logger = logging.getLogger(__name__)

from django.template import loader
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import AuthenticationForm


# USER IDENTITY HELPERS
def is_instructor(user):
    return Instructor.objects.filter(instructor_id=user.id).exists()

# TODO: Create this function when Learner is defined
# def is_learner(user):

def view_course(request, course_id):
    course = Course.objects.get(id=course_id)
    modules = course.modules.order_by('index').all()
    return render(request, 'courses/course_details.html', {
        'course': course,
        'modules': modules,
    })

def load_components(request, course_id, module_id):  
    module = Module.objects.get(id=module_id)
    components = module.getComponents().order_by("index")
    return render(request, 'courses/component_list.html', {
        'components': components,
    })

def view_enrolled_course(request):
    learner = Learner.objects.get(id=1) # to be changed after djando authentication done
    enrolled_course = []
    enrolments = Enrolment.objects.filter(learner=learner)
    for enrolment in enrolments:
        enrolled_course.append(Course.objects.get(enrolment=enrolment))
    return render(request, 'learner/enrolled_course_list.html', {
        'enrolled_course': enrolled_course,
    })

"""
Responsible for adding new courses

Utilized CourseForm which is in the file forms.py
"""
@user_passes_test(is_instructor)
def new_course(request):
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

# @login_required
def module_list(request, course_id):
    course = Course.objects.get(id=course_id)
    modules = course.modules.order_by('index').all()

    template = 'courses/module_list_learner.html'
    if is_instructor(request.user):
        template = 'courses/module_list_instructor.html'

    return render(request, template, {
        'modules': modules,
        'course': course
    })
        

    
@user_passes_test(is_instructor)
def edit_module(request, course_id, module_id=None):
    # TODO: Restrict this to only instructors who own the course the module belongs to

    course = Course.objects.get(id=course_id)

    # process form data
    if request.method == 'POST':
        form = ModuleForm(request.POST, course_id=course_id)
        if form.is_valid():
            # FIXME 
            form = form.save(commit=False)
            form.course = course
            form.save()
            url = reverse("module_list", kwargs={'course_id': course_id})
            return HttpResponseRedirect(url)

    # if module_id:
    #     module = Module.objects.get(id=module_id)

    form = ModuleForm(course_id=course_id)

    return render(request, 'courses/module_edit.html', {
        'course': course,
        # 'module': module,
        'action_word': 'Add',
        'form': form
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
