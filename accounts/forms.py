from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignupForm(forms.ModelForm):
    email = forms.EmailField(max_length=200, help_text='Required')
    #autobiography = forms.CharField(max_length=200)
    staff_id = forms.CharField(max_length=20)
    class Meta:
        model = User
        #fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'autobiography')
        fields = ('staff_id', 'email')

class LearnerRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')