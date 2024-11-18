from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Post
from django.db import models
from martor.widgets import AdminMartorWidget


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

admin.site.register(User, CustomUserAdmin)
admin.site.register(Post, PostAdmin)