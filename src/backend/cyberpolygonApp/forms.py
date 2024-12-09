from allauth.account.forms import SignupForm
from django.forms import ModelForm, widgets, Form
from .models import *
from martor.fields import MartorFormField

class CustomSignupForm(SignupForm):
    def signup(self, request, user):
        userRole = Role.objects.create(role_name = "user")
        user.id_role = userRole
        user.save()
        return user
    
class PostForm(Form):
    description = MartorFormField()

class PictureForm(ModelForm):
    class Meta:
        model = Picture
        fields = ('local_url', )
        widgets = {
            'image': widgets.ClearableFileInput(),
        }