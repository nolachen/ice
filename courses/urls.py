from django.urls import path
from courses import views

app_name = "courses"

urlpatterns = [
    path('<int:course_id>/details', views.view_course, name="view_course"),
    path('<int:course_id>/modules', views.module_list, name="module_list"),
    path('<int:course_id>/<int:module_id>/components', views.load_components, name="load_components"),
    # path('<int:course_id>/modules/<int:module_id>', views.module, name='module'),
    # path('<int:course_id>/modules/<int:module_id>/quiz', views.module_quiz, name='quiz'),
    path('<int:course_id>/new_module', views.edit_module, name='new_module'),
    path('new', views.new_course, name='new_course'),
]

# new_module page
# /modules/module_id page for edit, view, and delete