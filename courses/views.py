from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse, Http404, JsonResponse
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test

from courses.forms import CourseForm, ModuleForm, QuizForm, ImageUploadForm, TextComponentForm, SelectCategoryForm, AddExistingComponentsForm
from courses.models import Instructor, Learner, Course, Module, Quiz, Answer, QuizResult, Component, Enrollment

from datetime import date

import logging, json
logger = logging.getLogger(__name__)

# USER IDENTITY HELPERS
def is_instructor(user):
    return Instructor.objects.filter(user_id=user.id).exists()

def is_learner(user):
    return Learner.objects.filter(user_id=user.id).exists()

@login_required
def view_course(request, course_id):
    is_enrolled = False
    course = Course.objects.get(id=course_id)
    instructor = User.objects.get(id=course.instructor.user_id)
    modules = course.modules.order_by('index').all()
    available_modules = []
    locked_modules = []

    if is_instructor(request.user):
        available_modules = modules
    else:
        for module in modules:
            if Quiz.objects.filter(module=module).exists():
                quiz = Quiz.objects.get(module=module)
                quiz_result = QuizResult.objects.filter(learner__user=request.user, quiz_id=quiz.id)
                if quiz_result.filter(passed=True).exists():
                    available_modules.append(module)
                else:
                    available_modules.append(module)
                    module_index = list(modules).index(module) + 1
                    locked_modules = modules[module_index:]
                    break

    if is_learner(request.user):
        learner = Learner.objects.get(user_id=request.user.id)
        enrollments = Enrollment.objects.filter(learner=learner)
        if enrollments.filter(course=course).exists():
            is_enrolled = True
        else:
            available_modules = []
            locked_modules = modules
    
    return render(request, 'courses/course_details.html', {
        'user': request.user,
        'course': course,
        'instructor': instructor,
        'is_learner': is_learner(request.user),
        'is_enrolled': is_enrolled,
        'available_modules': available_modules,
        'locked_modules': locked_modules,
    })

@user_passes_test(is_learner)
def enroll_course(request, course_id):
    learner = Learner.objects.get(user_id=request.user.id)
    course = Course.objects.get(id=course_id)
    Enrollment.enroll(learner, course)
    return redirect('courses:view_enrolled_course')

def load_components(request, course_id, module_id):  
    module = Module.objects.get(id=module_id)
    components = Component.objects.filter(module_id=module_id).order_by("index")
    course = get_object_or_404(Course, id=course_id)
    quiz = Quiz.objects.get(module_id=module_id)

    if request.POST and is_instructor(request.user):
        form = AddExistingComponentsForm(request.POST, course_id=course_id)
        if form.is_valid():
            for component in form.cleaned_data['components']:
                module.add_component(component)

    add_components_form = AddExistingComponentsForm(course_id=course_id)
    context = {
        'is_learner': is_learner(request.user),
        'is_instructor': is_instructor(request.user),
        'components': components,
        'course': course,
        'module': module,
        'quiz': quiz,
        'add_components_form': add_components_form
    }
    return render(request, 'courses/component_list.html', context)

"""
View for all of the components in a course
"""
@user_passes_test(is_instructor)
def all_components(request, course_id):
    course = Course.objects.get(id=course_id)
    components = Component.objects.filter(course_id=course_id)
    return render(request, 'courses/components.html', {
        'components': components,
        'course': course
    })

@user_passes_test(is_instructor)
def edit_component(request, course_id, component_id):
    component = Component.objects.get(id=component_id)
    course = Course.objects.get(id=course_id)
    # Submitting edited component
    if request.method == 'POST':
        pass
    # Dispay the edit page
    else:
        return render(request, 'courses/component_edit.html', {
            'component': component,
            'course': course
        })

@user_passes_test(is_instructor)
def new_component(request, course_id, module_id=None, type=None, component_id=None):
    type_to_component_type = { 'image': Component.IMAGE, 'text': Component.TEXT }
    course = Course.objects.get(id=course_id)
    module = Module.objects.get(id=module_id) if module_id else None

    # You can only access this page if you own the course
    if request.user != course.instructor.user:
        raise Http404

    if component_id:
        component = Component.objects.get(id=component_id).get_child_component()
        component_type = component.component_type
    else:
        component = None
        component_type = type_to_component_type[type]

    component_url = (
        reverse("courses:load_components", kwargs={'course_id': course_id, 'module_id': module_id })
        if module_id
        else reverse("courses:all_components", kwargs={'course_id': course_id})
    ) 

    if request.method == 'POST':
        if component_type == Component.IMAGE:
            form = ImageUploadForm(request.POST, request.FILES, course_id=course_id, module_id=module_id, instance=component)
        elif component_type == Component.TEXT:
            form = TextComponentForm(request.POST, course_id=course_id, module_id=module_id, instance=component)
        else:
            raise Http404

        if form.is_valid():
            new_component = form.save(commit=False)
            new_component.course = course
            new_component.component_type = component_type
            new_component.save()

            if module:
                module.add_component(new_component)
            
            return HttpResponseRedirect(component_url)

    else:
        if component_type == Component.IMAGE:
            form = ImageUploadForm(instance=component, course_id=course_id, module_id=module_id)
        elif component_type == Component.TEXT:
            form = TextComponentForm(instance=component, course_id=course_id, module_id=module_id)
        else:
            raise Http404

    context = {
        'form': form,
        'course': course,
        'module': module,
        'cancel_url': component_url
    }
    if component:
        context['component'] = component
    
    return render(request, 'courses/component_edit.html', context) 

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
            new_course.instructor_id = Instructor.objects.get(user_id=request.user.id).id
            new_course.save()
            return HttpResponseRedirect(new_course.get_absolute_url())
        else:
            raise Http404
    else:
        form = CourseForm()
    return render(request, 'courses/course_form.html', {
        'form': form,
    })

@user_passes_test(is_instructor)
def deploy_course(request, course_id):
    course = Course.objects.get(id=course_id)
    course.deployed = True
    course.save()
    print(course_id)
    return redirect('courses:view_course', course_id)

def home(request):
    if request.POST:
        form = SelectCategoryForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['category'] == 'all':
                courses = Course.objects.all()
            else:
                courses = Course.objects.filter(category=form.cleaned_data['category'])
            return render(request, 'home.html', {
                'courses': courses,
                'form': form,
            })
    if is_instructor(request.user):
        courses = Course.objects.filter(instructor=Instructor.objects.get(user=request.user))
    else:
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
    learner = Learner.objects.get(user=request.user)
    not_completed_course = []
    completed_enrollments = Enrollment.objects.filter(learner=learner, completed=True).order_by('completed_date')
    cumulative_cecu = [0]
    for enrollment in completed_enrollments:
        cumulative_cecu.append(enrollment.course.cecu_value + cumulative_cecu[-1])
    completed_enrollments = zip(completed_enrollments, cumulative_cecu[1:])
    not_completed_enrollments = Enrollment.objects.filter(learner=learner, completed=False)
    for enrollment in not_completed_enrollments:
        not_completed_course.append(Course.objects.get(enrollment=enrollment))
    return render(request, 'courses/enrolled_course_list.html', {
        'completed_enrollments': completed_enrollments,
        'not_completed_course': not_completed_course,
    })

@user_passes_test(is_instructor)
def reorder_module(request, course_id):
    course = Course.objects.get(id=course_id)
    modules = course.modules.order_by('index').all()

    if request.user != course.instructor.user:
        raise Http404

    return render(request, 'courses/module_reorder.html', {
        'course': course,
        'modules': modules,
    })

@user_passes_test(is_instructor)
def reorder_module_save(request, course_id):
    course = Course.objects.get(id=course_id)

    if request.user != course.instructor.user:
        raise Http404
    
    if request.method == "POST" and request.is_ajax():
        new_module_order = request.POST.get('new_module_order')
        new_module_order_list = json.loads(new_module_order)
        new_module_order_list = list(map(int, new_module_order_list))
        # start from 1 because django cannot store 0
        counter = 1
        for item_id in new_module_order_list:
            module = Module.objects.get(id=item_id)
            module.index = counter
            module.save()
            counter += 1
        return JsonResponse(new_module_order, safe=False)

    return redirect('courses:view_course', course_id)

@user_passes_test(is_instructor)
def reorder_component(request, course_id, module_id):
    course = Course.objects.get(id=course_id)
    module = Module.objects.get(id=module_id)
    components = Component.objects.filter(module_id=module_id)

    if request.user != course.instructor.user:
        raise Http404

    return render(request, 'courses/component_reorder.html', {
        'course': course,
        'module': module,
        'components': components,
    })

@user_passes_test(is_instructor)
def reorder_component_save(request, course_id, module_id):
    course = Course.objects.get(id=course_id)

    if request.user != course.instructor.user:
        raise Http404
    
    if request.method == "POST" and request.is_ajax():
        new_comp_order = request.POST.get('new_comp_order')
        new_comp_order_list = json.loads(new_comp_order)
        new_comp_order_list = list(map(int, new_comp_order_list))
        # start from 1 because django cannot store 0
        counter = 1
        for item_id in new_comp_order_list:
            component = Component.objects.get(id=item_id)
            component.index = counter
            component.save()
            counter += 1
        return JsonResponse(new_comp_order, safe=False)

    return redirect('courses:view_course', course_id)

@user_passes_test(is_instructor)
def edit_module(request, course_id, module_id=None):
    course = get_object_or_404(Course, id=course_id)
    if module_id:
        module = get_object_or_404(Module, id=module_id)

    # You can only access this page if you own the course
    if request.user != course.instructor.user:
        raise Http404

    # process form data
    if request.method == 'POST':
        form = ModuleForm(request.POST, course_id=course_id)
        if form.is_valid():
            # FIXME 
            form = form.save(commit=False)
            form.course = course
            form.save()
            url = reverse("courses:module_list", kwargs={'course_id': course_id})
            return HttpResponseRedirect(url)

    # if module_id:
    #     module = Module.objects.get(id=module_id)

    # GET method
    else:
        form = ModuleForm(course_id=course_id)

    return render(request, 'courses/module_edit.html', {
        'course': course,
        # 'module': module,
        'action_word': 'Add',
        'form': form
    })

@user_passes_test(is_learner)
def take_quiz(request, course_id, module_id, quiz_id):
    learner = Learner.objects.get(user=request.user)
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
                # Check if the module is the last module
                module = Module.objects.get(id=module_id)
                course = Course.objects.get(id=course_id)
                if (module == course.modules.order_by('index').last()):
                    enrollment = Enrollment.objects.get(learner=learner, course=course)
                    enrollment.completed = True
                    enrollment.completed_date = date.today()
                    enrollment.save()

                    learner.award_cecu_credit(course.cecu_value)
                    mail_subject = 'You are awarded with ' + str(course.cecu_value) + ' credits!'
                    message = render_to_string('courses/award_cecu_value_email.html', {
                        'user': request.user,
                        'course': course,
                    })
                    to_email = request.user.email
                    email = EmailMessage(
                                mail_subject, message, to=[to_email]
                    )
                    email.send()
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

# def view_component(request, course_id):
#     course = Course.objects.get(id=course_id)
#     template = 'courses/component_details.html'

#     return render(request, template, {
#         'course': course
#     })

# @user_passes_test(is_instructor)
# def upload_image(request, course_id):
#     course = Course.objects.get(id=course_id)

#     if request.method == 'POST':
#         form = ImageUploadForm(request.POST, request.FILES, course_id=course_id)
#         if form.is_valid():
#             form = form.save(commit=False)
#             form.course = course
#             form.save()
#             return render(request, 'courses/component_details.html', {
#                 'course_id': course_id,
#                 'course': course,
#                 'form': form,
#             })
#         else:
#             raise Http404

#         return render(request, 'courses/component_details.html', {
#             'course_id': course_id,
#             'course': course,
#         })
#     else:
#         form = ImageUploadForm(request.POST, request.FILES, course_id=course_id)
    
#     return render(request, 'courses/create_image_component.html', { 
#         'form': form,
#         'course_id': course_id, 
#         'course': course,
#     })
