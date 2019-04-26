from django import forms
from courses.models import Course, Module, Component, Category, Question, Answer, Choice, Quiz, ImageComponent, TextComponent
import logging
logger = logging.getLogger(__name__)

# Base form to add Bootstrap 'form-control' class to every input
class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for _, field in self.fields.items():
            if getattr(field.widget, 'input_type', None) == 'file':
                field.widget.attrs['class'] = 'form-control-file'
            else:     
                field.widget.attrs['class'] = 'form-control'

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
        # self.fields['textcomponents'] = forms.ModelMultipleChoiceField(
        #     required=False,
        #     queryset=course.textcomponents.filter(module__isnull=True)
        # )
        # self.fields['imagecomponents'] = forms.ModelMultipleChoiceField(
        #     required=False,
        #     queryset=course.imagecomponents.filter(module__isnull=True)
        # )
        self.fields['quiz'] = forms.ModelChoiceField(
            required=False,
            queryset=course.quizzes.filter(module__isnull=True)
        )

class QuizForm(forms.Form):
    def __init__(self, quiz_id, *args, **kwargs):
        quiz = Quiz.objects.get(id=quiz_id)
        # If I dont use [:quiz.num_questions], then everything will be fine,
        # otherwise the score is calculated randomly, even same choices are selected,
        # the result score differs
        questions = quiz.question_set.all().order_by('?')
        super(QuizForm, self).__init__(*args, **kwargs)
        for question in questions:
            choices = []
            for choice in Choice.objects.filter(question_id=question.id):
                choices.append((choice.id, choice.choice_text))
            self.fields[str(question.id)] = forms.ChoiceField(label=question.question_text, required=False, choices=choices, widget=forms.RadioSelect)
        self.fields.pop('1')
        self.fields.pop('2')

class ComponentForm(BaseForm):
    def __init__(self, *args, **kwargs):
        course_id = kwargs.pop('course_id')
        module_id = kwargs.pop('module_id')
        if not course_id:
            raise RuntimeError('Need course_id for ComponentForm')
        super(ComponentForm, self).__init__(*args, **kwargs)        
        if module_id:
            del self.fields['module']
        else:
            self.fields['module'].queryset = Module.objects.filter(course=course_id)
            self.fields['module'].help_text = 'Optional'


    class Meta:
        model = Component
        fields = ('module', 'title')
        
class ImageUploadForm(ComponentForm):
    def __init__(self, *args, **kwargs):
        super(ImageUploadForm, self).__init__(*args, **kwargs)

    class Meta(ComponentForm.Meta):
        model = ImageComponent
        fields = ComponentForm.Meta.fields + ('image_details', 'image')
        labels = {
            'image_details': 'Description'
        }

class TextComponentForm(ComponentForm):
    def __init__(self, *args, **kwargs):
        super(TextComponentForm, self).__init__(*args, **kwargs)

    class Meta(ComponentForm.Meta):
        model = TextComponent
        fields = ComponentForm.Meta.fields + ('text_passage',)

class SelectCategoryForm(forms.Form):
    def __init__(self, *args, **kwargs):
        categories = Category.objects.all()
        choices = [('all', ('All'))]
        super(SelectCategoryForm, self).__init__(*args, **kwargs)
        for category in categories:
            choices.append((category.id, category.name))
        self.fields['category'] = forms.ChoiceField(choices=choices)

class AddExistingComponentsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        course_id = kwargs.pop('course_id')
        if not course_id:
            raise RuntimeError('Need course_id for ComponentForm')
        super(AddExistingComponentsForm, self).__init__(*args, **kwargs)        

        self.fields['components'] = forms.ModelMultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            queryset=Component.objects.filter(course=course_id, module__isnull=True)
        )