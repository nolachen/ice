from django.urls import path
from courses import views

urlpatterns = [
    path('<int:course_id>/detail', views.view_course),
    path('<int:course_id>/modules', views.module_list, name="module_list"),
    # path('<int:course_id>/modules/<int:module_id>', views.module, name='module'),
    # path('<int:course_id>/modules/<int:module_id>/quiz', views.module_quiz, name='quiz'),
    path('<int:course_id>/new_module', views.edit_module, name='new_module'),
]

# new_module page
# /modules/module_id page for edit, view, and delete