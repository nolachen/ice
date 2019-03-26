from django import forms

from courses.models import Course, Module, Component

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

