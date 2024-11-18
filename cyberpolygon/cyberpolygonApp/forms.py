from allauth.account.forms import SignupForm
from django import forms
from .models import *
from martor.fields import MartorFormField

class CustomSignupForm(SignupForm):
    def signup(self, request, user):
        userRole = Role.objects.create(role_name = "user")
        user.id_role = userRole
        user.save()
        return user
    
class PostForm(forms.Form):
    description = MartorFormField()