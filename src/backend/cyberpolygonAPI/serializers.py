from cyberpolygonApp.models import *
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from rest_framework import serializers

import datetime


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'telegram_id', 'user_data', 'password')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('__all__')


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'created_at')


class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ('id', 'task_id', 'user_id', 'comment', 'rating', 'created_at')


class UserAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAvatar
        fields = ('__all__')


class TestSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=False)

    class Meta:
        model = Test
        fields = ['title', 'description', 'created_at']

    def validate(self, title):
        if Test.objects.filter(title=title):
            raise serializers.ValidationError(
                "Такой тест уже существует")
        return title

    def save(self, data):
        test = Test.objects.create(title=data['title'], description=data['description'],
                                   created_at=datetime.date.today())
        return test


class VagrantSerializer(serializers.Serializer):
    class Meta:
        model = UserDoingTask
        fields = '__all__'