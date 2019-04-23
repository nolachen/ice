from django.urls import path
from courses import views

app_name = "courses"

urlpatterns = [
    path('<int:course_id>/details', views.view_course, name="view_course"),
    path('<int:course_id>/components', views.all_components, name="all_components"),
    path('<int:course_id>/component/<int:component_id>/edit', views.new_component, name="edit_component"),
    path('<int:course_id>/component/new/<str:type>', views.new_component, name="new_component"),
    path('<int:course_id>/modules', views.module_list, name="module_list"),
    path('<int:course_id>/modules/<int:module_id>/components', views.load_components, name="load_components"),
    path('<int:course_id>/modules/<int:module_id>/quiz/<int:quiz_id>/', views.take_quiz, name="take_quiz"),
    # path('<int:course_id>/modules/<int:module_id>', views.module, name='module'),
    # path('<int:course_id>/modules/<int:module_id>/quiz', views.module_quiz, name='quiz'),
    path('<int:course_id>/new_module', views.edit_module, name='new_module'),
    path('<int:course_id>/reorder_module', views.reorder_module, name='reorder_module'),
    path('<int:course_id>/reorder_module_save', views.reorder_module_save, name='reorder_module_save'),
    path('new', views.add_course, name='add_course'),
    path('<int:course_id>/deploy', views.deploy_course, name='deploy_course'),
    # path('<int:course_id>/create_image_component/', views.upload_image, name='upload_image'),
    # path('<int:course_id>/component_details', views.view_component, name='view_component'),
    path('<int:course_id>/enroll_course', views.enroll_course, name='enroll_course'),
    path('enrolled', views.view_enrolled_course, name='view_enrolled_course'),
]

# new_module page
# /modules/module_id page for edit, view, and delete