from django import forms
from django.contrib.auth.forms import UserCreationForm
from Courses.models import Instructor

class InstructorSignupForm(UserCreationForm):
    #email = forms.EmailField(max_length=200, help_text='Required')
    class Meta:
        model = Instructor
        fields = ('username', 'first_name', 'last_name' 'password1', 'password2')