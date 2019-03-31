from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse

from courses.forms import CourseForm, ModuleForm, QuizForm
from courses.models import Instructor, Course, Module, Quiz, Answer, QuizResult

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

def view_course(request,course_id):
	courseObj = Course.objects.get(id=course_id)
	x = 3
	modules = Module.objects.filter(course=courseObj).order_by("index")

	template=loader.get_template('courses/course_info.html')
	context={'course': courseObj, 'modules': modules, 'enrollStatus': x, 'participant_id': request.user.id }
	return HttpResponse(template.render(context,request))

'''def course_detail(request, course_id):
    course = Course.objects.get(id=course_id)
    return render(request, 'courses/course_detail.html', {
        'course': course,
    })'''

def loadComponents(request, course_id, module_id):
    courseObj = Course.objects.get(id=course_id)    
    moduleObj = Module.objects.get(id=module_id)
    component_list = moduleObj.getComponents().order_by("index")
    context = {'components': component_list}
    print (context)
    template = loader.get_template('courses/component_list.html')
    return HttpResponse(template.render(context,request))

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
    # Check if Learner already passed the quiz
    if (QuizResult.objects.filter(learner_id=request.user.id).exists()
            and QuizResult.objects.filter(quiz_id=quiz.id).exists()):
        return render(request, 'quiz/take_quiz.html', {
            "passed": True,
        })

    questions = quiz.question_set.all()
    if request.method == "POST":
        form = QuizForm(quiz_id, request.POST)
        if form.is_valid():
            passed = False
            num_of_correct = 0
            for question in questions:
                if ( int(form.cleaned_data[str(question.id)]) == (Answer.objects.get(question_id=question.id).correct_answer_id)):
                    num_of_correct += 1
            if (num_of_correct >= quiz.num_questions * quiz.passing_score):
                passed = True
                QuizResult.record_passed_quiz(quiz.id, request.user.id)

        return render(request, 'quiz/result.html', {
            "course_id": quiz.course_id,
            "quiz": quiz,
            "passed": passed,
        })
    else:
        form = QuizForm(quiz_id)
    return render(request, 'quiz/take_quiz.html', {
        "quiz": quiz,
        "form": form,
    })