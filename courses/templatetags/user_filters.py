from django import template
from courses.models import Instructor

register = template.Library()

@register.filter(name="is_instructor")
def is_instructor(user):
    return Instructor.objects.filter(instructor_id=user.id).exists()
