from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.sign_up.as_view(), name='singup'),
]