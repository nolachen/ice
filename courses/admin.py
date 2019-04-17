from django.contrib import admin

from courses.models import *

# Register your models here.
admin.site.register(Course)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Module)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(TextComponent)
admin.site.register(ImageComponent)
admin.site.register(Category)
