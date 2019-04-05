from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignupForm, LearnerRegisterForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage

# Create your views here.
class old_signup(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/old_signup.html'

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

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        #user.is_active = True
        #user.save()
        return register_learner(request, user)
    else:
        return HttpResponse('Activation link is invalid!')

def register_learner(request, user):
    print('userid:', user.id)
    if request.method=='POST':
        form = LearnerRegisterForm(request.POST)
        if form.is_valid():
            print('username:', form.cleaned_data['username'])
            user.username = form.cleaned_data['username']
            user.set_password(form.cleaned_data['password2'])
            user.is_active = True
            user.save()
        else:
            raise Http404
        return HttpResponse('Registered')
    else:
        form = LearnerRegisterForm()
    return render(request, 'registration/register.html', {
        'form': form
    })
