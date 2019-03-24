from django.urls import path
from courses import views

urlpatterns = [
    path('<int:course_id>', views.course_detail),
    path('<int:course_id>/create_module', views.create_module)
]