from rest_framework import serializers
from .models import *
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
import datetime

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'telegram_id', 'user_data')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name')

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


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, write_only=True)
    username = serializers.CharField(required=True, write_only=True)
    password1 = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def validate_email(self, email):
        if User.objects.filter(email=email):
            raise serializers.ValidationError(
                "Пользователь с такой почтой уже существует")
        return email

    def validate_username(self, username):
        if User.objects.filter(username=username):
            raise serializers.ValidationError(
                "Пользователь с таким именем уже существует")
        return username

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Пароли не совпадают")
        return data

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        setup_user_email(request, user, [])
        return user
    
class LoginSerializer(serializers.Serializer):
#       email = serializers.EmailField()
       username = serializers.CharField()
       password = serializers.CharField(write_only=True)

from rest_framework import serializers
from .models import Test
import datetime

class TestSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=False)

    class Meta:
        model = Test
        fields = ['title', 'description', 'created_at']

    # Валидация для проверки уникальности заголовка
    def validate(self, data):
        if Test.objects.filter(title=data['title']).exists():
            raise serializers.ValidationError("Такой тест уже существует")
        return data

    # Метод save для создания объекта Test
    def create(self, validated_data):
        # Устанавливаем дату создания
        validated_data['created_at'] = datetime.date.today()
        # Создаем объект Test
        return Test.objects.create(**validated_data)
    
class AnswerSerializer(serializers.ModelSerializer):
    is_correct = serializers.BooleanField(required=True)

    class Meta:
        model = Answer
        fields = ['answer_text', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ['question_text', 'answers']

from rest_framework import serializers
from .models import CorrectAnswer, Answer, Question

class CorrectAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorrectAnswer
        fields = ['question_id', 'answer_id']

