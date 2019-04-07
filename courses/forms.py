from django import forms
from courses.models import Course, Module, Component, Question, Answer, Choice, Quiz, ImageComponent
import logging
logger = logging.getLogger(__name__)

"""
For adding new courses
"""
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'cecu_value', 'description', 'category']

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
    def __init__(self, quiz_id, *args, **kwargs):
        quiz = Quiz.objects.get(id=quiz_id)
        questions = quiz.question_set.all()
        super(QuizForm, self).__init__(*args, **kwargs)
        for question in questions:
            field_name = question.id
            choices = []
            index = 0
            for choice in Choice.objects.filter(question_id=question.id):
                choices.append((choice.id, choice.choice_text))
                index = index + 1
            self.fields[str(question.id)] = forms.ChoiceField(label=question.question_text, required=True, 
                                        choices=choices, widget=forms.RadioSelect)

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ImageComponent
        fields = ('image_details', 'image')
    
    def __init__(self, *args, **kwargs):
        course_id = kwargs.pop('course_id')
        if not course_id:
            raise RuntimeError('Need course_id for ImageUploadForm')

        super(ImageUploadForm, self).__init__(*args, **kwargs)
