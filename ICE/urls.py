"""ICE URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from django.conf import settings
from courses.views import *
from accounts.views import *

urlpatterns = [
    path('', home),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', signup, name='signup'),
    path('course_list/', course_list),
    path('admin/', admin.site.urls),
    path('course_add/', course_add),
    path('courses/', include('courses.urls'))
    path('take_quiz/<int:quiz_id>/', take_quiz),
    path('course_detail/<int:course_id>/', view_course, name='view_course'),
    path('course_detail/<int:course_id>/<int:module_id>/loadComponents/', loadComponents, name='loadComponents'),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()