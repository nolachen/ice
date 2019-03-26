from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponseRedirect
from django.template import loader

from django.contrib.auth.models import User

from courses.forms import CourseForm, QuizForm
from courses.models import *

import logging
logger = logging.getLogger(__name__)

def course_detail(request, course_id):
    course = Course.objects.get(id=course_id)
    return render(request, 'courses/course_detail.html', {
        'course': course,
    })

def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {
        'courses': courses,
    })

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
    quiz = Quiz.objects.filter(id=quiz_id)
    if request.method == "POST":
        # To be Implemented
        """
        questions = quiz.question_set.all()
        form = QuizForm(request.POST, questions)
        if form.is_valid(): ## Will only ensure the option exists, not correctness.
            attempt = form.save()
            return redirect(attempt)
        """
        return render(request, 'quiz/result.html')
    else:
        questions = Question.objects.filter(quiz_id=quiz_id)
        form = QuizForm(questions)
    return render(request, 'quiz/take_quiz.html', {
        "form": form,
        "questions": questions,
    })
