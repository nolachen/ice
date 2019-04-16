from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignupForm(forms.ModelForm):
    staff_id = forms.CharField(min_length=8, max_length=8)
    class Meta:
        model = User
        fields = ('staff_id',)

class InviteForm(forms.ModelForm):
    email = forms.EmailField(max_length=200)
    class Meta:
        model = User
        fields = ('email',)

class LearnerRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

class InstructorRegisterForm(UserCreationForm):
    autobiography = forms.CharField(max_length=400)
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2', 'autobiography')

class RestrictUserForm(forms.Form):
    username = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True, is_superuser=False).order_by('username'))

class UnrestrictUserForm(forms.Form):
    username = forms.ModelChoiceField(queryset=User.objects.filter(is_active=False, is_superuser=False).order_by('username')) 