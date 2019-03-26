from django import forms

from courses.models import Course, Module, Component, Question, Answer

import logging
logger = logging.getLogger(__name__)

"""
For adding new courses
"""
class CourseForm(forms.ModelForm):

    class Meta:
        model = Course
        fields = ['name', 'description']

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title']

    def __init__(self, *args, **kwargs):
        course_id = kwargs.pop('course_id')
        if not course_id:
            raise RuntimeError('Need course_id for ModuleForm')

        super(ModuleForm, self).__init__(*args, **kwargs)
        course = Course.objects.get(id=course_id)
        self.fields['textcomponents'] = forms.ModelMultipleChoiceField(
            required=False,
            queryset=course.textcomponents.filter(module__isnull=True)
        )
        self.fields['imagecomponents'] = forms.ModelMultipleChoiceField(
            required=False,
            queryset=course.imagecomponents.filter(module__isnull=True)
        )
        self.fields['quiz'] = forms.ModelChoiceField(
            required=False,
            queryset=course.quizzes.filter(module__isnull=True)
        )

class QuizForm(forms.Form):
    def __init__(self, questions, *args, **kwargs):
        self.questions = questions
        
        super(QuizForm, self).__init__(*args, **kwargs)
        for question in questions:
            choices = (
                ('A', 'choice 1'),
                ('B', 'choice 2'),
                ('C', 'choice 3'),
                ('D', 'choice 4'),
            )
            
            """
            for answer in Answer.objects.filter(question_id=question.question_id):
                choices.append(answer.answer_text)
            ## May need to pass some initial data, etc:
            """
            self.fields[question] = forms.ChoiceField(label=question, required=True, 
                                        choices=choices, widget=forms.RadioSelect)
    def save(self):
        pass
