from django.contrib.auth.models import AbstractUser
import jsonfield
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Model, OneToOneField
from django.contrib.auth.base_user import BaseUserManager
from martor.models import MartorField
from .utils import upload_image_info
import os
import uuid


class CustomUserManager(BaseUserManager):

    def create_user(self, email, username, password, **extra_fields):

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        if not username:
            raise ValueError("Username shouldn't be empty")
        if not password:
            raise ValueError("Password shoudn't be empty")

        user = self.model(**extra_fields)
        if email:
            email = self.normalize_email(email)
            user.email = email
        user.set_password(password)
        userRole = Role.objects.create(role_name="user")
        user.id_role = userRole
        user.save(using=self.db)
        return user

    def create_superuser(self, email, password, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        user = self.model(**extra_fields)
        if email:
            email = self.normalize_email(email)
            user.email = email
        user.set_password(password)
        adminRole = Role.objects.create(role_name="admin")
        user.id_role = adminRole
        user.save(using=self.db)
        return user


class User(AbstractUser):
    user_data = jsonfield.JSONField()
    id_role = models.ForeignKey('Role', on_delete=models.PROTECT, null=True)
    telegram_id = models.CharField(max_length=50, unique=True, null=True)
    verification_code = models.CharField(max_length=6, null=True, blank=True)

    REQUIRED_FIELDS = ["email"]
    objects = CustomUserManager()


class Role(models.Model):
    role_name = models.TextField(max_length=50, default="user")
    description = models.TextField()


class Category(models.Model):
    name = models.TextField(max_length=50)


class Task(models.Model):
    id = models.AutoField(primary_key=True, db_index=True)
    title = models.TextField(max_length=100, unique=True, null=False)
    description = models.TextField()
    points = models.IntegerField
    created_at = models.DateField(auto_now_add=True)


class Media(models.Model):
    file_path = models.TextField(max_length=1024)
    file_hash = models.TextField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.file_path


class UserDoingTask(models.Model):
    task = models.ForeignKey('Task', on_delete=models.PROTECT)
    user = models.ForeignKey('User', on_delete=models.PROTECT)
    flag = models.TextField(max_length=100)
    vagrant_password = models.TextField(max_length=50)
    is_active = models.BooleanField()


class Comments(models.Model):
    id = models.AutoField(primary_key=True, db_index=True)
    task_id = models.ForeignKey('Task', on_delete=models.PROTECT)
    user_id = models.ForeignKey('User', on_delete=models.PROTECT)
    comment = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class UserAvatar(models.Model):
    user_id = OneToOneField('User', on_delete=models.PROTECT)
    media = GenericRelation('Media')
    # image_path = models.TextField(max_length=255)
    # image_hash = models.TextField(max_length=255)
    created_at = models.DateField()


class Post(models.Model):
    id = models.AutoField(primary_key=True, db_index=True)
    title = models.CharField(max_length=100, unique=True, null=False)
    description = MartorField()
    media = GenericRelation('Media')

    def __str__(self):
        return f"{self.id}, {self.title}"


class Test(models.Model):
    id = models.AutoField(primary_key=True, db_index=True)
    title = models.CharField(max_length=100, unique=True, null=False)
    description = models.TextField(max_length=255)
    created_at = models.DateField(auto_now_add=True)


    def __str__(self):
        return f"{self.title}"


class Question(models.Model):
    id = models.AutoField(primary_key=True, db_index=True)
    test_id = models.ForeignKey('Test', on_delete=models.PROTECT)
    question_text = models.TextField()
    created_at = models.DateField()


class Answer(models.Model):
    id = models.AutoField(primary_key=True, db_index=True)
    question_id = models.ForeignKey('Question', on_delete=models.PROTECT)
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)


class CorrectAnswer(models.Model):
    question_id = models.ForeignKey('Question', on_delete=models.PROTECT)
    answer_id = models.ForeignKey('Answer', on_delete=models.PROTECT)



def upload_to(instance, filename):
    image_info = upload_image_info(filename)
    instance.image_name = image_info["img_uuid"]
    instance.url_to_upload = image_info["img_url"]
    relative_path = instance.url_to_upload.rfind('images/')
    return instance.url_to_upload[relative_path:]

class Picture(models.Model):
    local_url = models.ImageField(upload_to=upload_to)
    image_name = models.CharField(max_length=10)
    url_to_upload = models.CharField(max_length=200, default='')

    def __str__(self):
        return self.image_name

    def upload_image(image):
        image_info = upload_image_info(image)
        image_name = image_info["img_uuid"]
        picture = Picture.objects.create(image_name=image_name, url_to_upload=image_info["img_url"])
        return picture
    
    def delete(self, using=None, keep_parents=False):
        os.remove(self.url_to_upload)
        super().delete(using=using, keep_parents=keep_parents)


