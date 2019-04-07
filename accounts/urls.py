from django.urls import path, re_path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('signup', views.signup, name='signup'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
]