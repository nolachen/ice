from django import template
from courses.models import Instructor, Learner

register = template.Library()

@register.filter(name="is_instructor")
def is_instructor(user):
    return Instructor.objects.filter(user_id=user.id).exists()

@register.filter(name="is_learner")
def is_learner(user):
    return Learner.objects.filter(user_id=user.id).exists()

@register.filter(name="is_admin")
def is_admin(user):
    return user.is_superuser