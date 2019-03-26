from django import forms

from courses.models import Course, Module

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
        fields = ('title')

    def __init__(self, course_id, *args, **kwargs):
        super(ModuleForm, self).__init__(*args, **kwargs)
        course = Course.objects.get(id=course_id)
        self.components = forms.ModelMultipleChoiceField(
            required=False
            queryset=course.components
        )

