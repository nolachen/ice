from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import SignupForm, InviteForm, LearnerRegisterForm, InstructorRegisterForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage

from courses.models import Learner, Instructor

# USER IDENTITY HELPERS
def is_superuser(user):
    return User.objects.get(id=user.id).is_superuser == 1

"""
For Learners only, Staff ID needed.
"""
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.is_staff = True
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('registration/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')
        else:
            raise Http404
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {
        'form': form
    })

"""
For sending out invitation email (which contains a token link) to Instructors
"""
@login_required
@user_passes_test(is_superuser)
def invite(request):
    if request.method == 'POST':
        form = InviteForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.is_staff = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('registration/invite_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponse('Invitation sent')
        else:
            raise Http404
    else:
        form = InviteForm()
    return render(request, 'registration/invite.html', {
        'form': form
    })

"""
For activating both Learners and Instructors account,
they will be disginushed according to the 'is_staff' attribute
"""
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        if user.is_staff == True:
            return register_learner(request, user)
        else:
            return register_instructor(request, user)
    else:
        return HttpResponse('Activation link is invalid!')

def register_learner(request, user):
    if request.method == 'POST':
        form = LearnerRegisterForm(request.POST)
        if form.is_valid():
            user.username = form.cleaned_data['username']
            user.set_password(form.cleaned_data['password2'])
            user.is_active = True
            user.save()
            learner = Learner(learner_id=user.id)
            learner.save()
        else:
            raise Http404
        return redirect('login')
    else:
        form = LearnerRegisterForm()
    return render(request, 'registration/register.html', {
        'form': form
    })

def register_instructor(request, user):
    if request.method == 'POST':
        form = InstructorRegisterForm(request.POST)
        if form.is_valid():
            user.username = form.cleaned_data['username']
            user.set_password(form.cleaned_data['password2'])
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.is_active = True
            user.save()
            instructor = Instructor(instructor_id=user.id)
            instructor.autobiography = form.cleaned_data['autobiography']
            instructor.save()
        else:
            raise Http404
        return redirect('login')
    else:
        form = InstructorRegisterForm()
    return render(request, 'registration/register.html', {
        'form': form
    })