from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse, Http404
from django.template import loader
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse

from courses.forms import CourseForm, ModuleForm, QuizForm, ImageUploadForm, TextComponentForm, SelectCategoryForm
from courses.models import *

import logging
logger = logging.getLogger(__name__)

from django.template import loader
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import AuthenticationForm

from django.urls import reverse_lazy


# USER IDENTITY HELPERS
def is_instructor(user):
    return Instructor.objects.filter(instructor_id=user.id).exists()

def is_learner(user):
    return Learner.objects.filter(learner_id=user.id).exists()

@login_required
def view_course(request, course_id):
    course = Course.objects.get(id=course_id)
    modules = course.modules.order_by('index').all()
    available_modules = []
    locked_modules = []
    for module in modules:
        quiz = Quiz.objects.get(module=module)
        quiz_result = QuizResult.objects.filter(learner__learner=request.user, quiz_id=quiz.id)
        if is_instructor(request.user) or quiz_result.filter(passed=True).exists():
            available_modules.append(module)
        else:
            available_modules.append(module)
            module_index = list(modules).index(module) + 1
            locked_modules = modules[module_index:]
            break
    print(available_modules)
    print(locked_modules)
    return render(request, 'courses/course_details.html', {
        'course': course,
        'available_modules': available_modules,
        'locked_modules': locked_modules,
    })

def load_components(request, course_id, module_id):  
    module = Module.objects.get(id=module_id)
    components = module.getComponents().order_by("index")
    quiz = Quiz.objects.get(module_id=module_id)
    return render(request, 'courses/component_list.html', {
        'components': components,
        'course_id': course_id,
        'module_id': module_id,
        'quiz': quiz,
    })

"""
View for all of the components in a course
"""
@user_passes_test(is_instructor)
def all_components(request, course_id):
    course = Course.objects.get(id=course_id)
    components = course.get_components()
    return render(request, 'courses/components.html', {
        'components': components,
        'course': course
    })

@user_passes_test(is_instructor)
def edit_component(request, course_id, component_id):
    component = Component.objects.get(id=component_id)
    # Submitting edited component
    if request.method == 'POST':
        pass
    # Dispay the edit page
    else:
        return render(request, 'courses/component_edit.html', {
            'component': component
        })

@user_passes_test(is_instructor)
def new_component(request, course_id, type):
    course = Course.objects.get(id=course_id)

    if request.method == 'POST':
        if type == 'image':
            form = ImageUploadForm(request.POST, request.FILES, course_id=course_id)
        elif type == 'text':
            form = TextComponent(request.POST, course_id=course_id)
        else:
            raise Http404

        if form.is_valid():
            form = form.save(commit=False)
            form.course = course
            form.save()
            return render(request, 'courses/component_details.html', {
                'course_id': course_id,
                'course': course,
                'form': form,
            })
        else:
            raise Http404

    else:
        if type == 'image':
            form = ImageUploadForm(course_id=course_id)
        elif type == 'text':
            form = TextComponent(course_id=course_id)
        else:
            raise Http404
        
        return render(request, 'courses/create_image_component.html', { 
        'form': form,
            'course_id': course_id, 
            'course': course,
        }) 

"""
Responsible for adding new courses

Utilized CourseForm which is in the file forms.py
"""
@user_passes_test(is_instructor)
def add_course(request):
    if request.POST:
        form = CourseForm(request.POST)
        if form.is_valid():
            new_course = form.save(commit=False)
            new_course.instructor_id = Instructor.objects.get(instructor_id=request.user.id).id
            new_course.save()
            return HttpResponseRedirect(new_course.get_absolute_url())
        else:
            raise Http404
    else:
        form = CourseForm()
    return render(request, 'courses/course_form.html', {
        'form': form,
    })

def home(request):
    if request.POST:
        form = SelectCategoryForm(request.POST)
        if form.is_valid():
            courses = Course.objects.filter(category=form.cleaned_data['category'])
            #form = SelectCategoryForm()
            return render(request, 'home.html', {
                'courses': courses,
                'form': form,
            })
    courses = Course.objects.all()
    form = SelectCategoryForm()
    return render(request, 'home.html', {
        'courses': courses,
        'form': form,
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

@user_passes_test(is_learner)
def view_enrolled_course(request):
    learner = Learner.objects.get(learner=request.user)
    enrolled_course = []
    enrollments = Enrollment.objects.filter(learner=learner)
    for enrollment in enrollments:
        enrolled_course.append(Course.objects.get(enrollment=enrollment))
    return render(request, 'courses/enrolled_course_list.html', {
        'enrolled_course': enrolled_course,
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
        else:
            raise Http404

    # if module_id:
    #     module = Module.objects.get(id=module_id)

    form = ModuleForm(course_id=course_id)

    return render(request, 'courses/module_edit.html', {
        'course': course,
        # 'module': module,
        'action_word': 'Add',
        'form': form
    })

@user_passes_test(is_learner)
def take_quiz(request, course_id, module_id, quiz_id):
    learner = Learner.objects.get(learner=request.user)
    quiz = Quiz.objects.get(id=quiz_id)
    # Check if Learner already passed the quiz
    quiz_result = QuizResult.objects.filter(learner=learner, quiz_id=quiz.id)
    if quiz_result.filter(passed=True).exists():
        return render(request, 'quiz/take.html', {
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
            if (num_of_correct >= quiz.passing_score * quiz.num_questions / 100):
                passed = True
            else:
                passed = False
            
            QuizResult.new_record(quiz.id, learner, num_of_correct / quiz.num_questions * 100, passed)
        else:
            raise Http404

        return render(request, 'quiz/result.html', {
            "course_id": quiz.course_id,
            "quiz": quiz,
            "passed": passed,
            "score": num_of_correct / quiz.num_questions * 100,
            "passing_score": quiz.passing_score * quiz.num_questions,
        })
    else:
        form = QuizForm(quiz_id)
    return render(request, 'quiz/take.html', {
        "quiz": quiz,
        "form": form,
    })

def view_component(request, course_id):
    course = Course.objects.get(id=course_id)
    template = 'courses/component_details.html'

    return render(request, template, {
        'course': course
    })

@user_passes_test(is_instructor)
def upload_image(request, course_id):
    course = Course.objects.get(id=course_id)

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES, course_id=course_id)
        if form.is_valid():
            form = form.save(commit=False)
            form.course = course
            form.save()
            return render(request, 'courses/component_details.html', {
                'course_id': course_id,
                'course': course,
                'form': form,
            })
        else:
            raise Http404

        return render(request, 'courses/component_details.html', {
            'course_id': course_id,
            'course': course,
        })
    else:
        form = ImageUploadForm(request.POST, request.FILES, course_id=course_id)
    
    return render(request, 'courses/create_image_component.html', { 
        'form': form,
        'course_id': course_id, 
        'course': course,
    })
