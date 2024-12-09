from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from django.db import models
from martor.widgets import AdminMartorWidget
from .forms import *

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        *UserAdmin.fieldsets,  
        (                      
            'verification',
            {
                'fields': (
                    'telegram_id', 'verification_code'
                ),
            },
        ),
    )
class PostAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }

@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        if obj:
            kwargs['fields'] = ['local_url', 'image_name', 'url_to_upload',]
        else:
            kwargs['fields'] = ['local_url',]
        return super(PictureAdmin, self).get_form(request, obj, **kwargs)

@admin.register(Test, Question, Answer, CorrectAnswer)
class TestsAdmin(admin.ModelAdmin):
    pass

@admin.register(Task, UserDoingTask)
class TasksAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, CustomUserAdmin)
admin.site.register(Post, PostAdmin)