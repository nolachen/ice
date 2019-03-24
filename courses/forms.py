from django import forms

from courses.models import Course

"""
For adding new courses
"""
class CourseForm(forms.ModelForm):

    class Meta:
        model = Course
        fields = ['name', 'description']