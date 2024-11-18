from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from .serializers import *
from .utils import markdown_find_images, get_or_none
from rest_framework.response import Response
from django.http import HttpResponse
from django.conf import settings
from rest_framework import status
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.yandex.views import YandexAuth2Adapter
from allauth.socialaccount.providers.telegram.views import LoginView
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.views import ObtainAuthToken
from django.views.decorators.csrf import requires_csrf_token, csrf_exempt
from dj_rest_auth.registration.views import SocialLoginView
from django_otp.plugins.otp_totp.models import TOTPDevice
from .verification import send_verification_code_to_telegram
from martor.utils import LazyEncoder
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.template import loader
import requests
import datetime
import qrcode
import io
import base64
import json
import os
import uuid

LOCALHOST =  "http://127.0.0.1:7000/"

class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CategoryListCreate(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class TaskListCreate(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class TaskRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class CommentsListCreate(generics.ListCreateAPIView):
    queryset = Comments.objects.all()
    serializer_class = CommentsSerializer

class CommentsRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comments.objects.all()
    serializer_class = CommentsSerializer

class UserAvatarListCreate(generics.ListCreateAPIView):
    queryset = UserAvatar.objects.all()
    serializer_class = UserAvatarSerializer

class UserAvatarRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserAvatar.objects.all()
    serializer_class = UserAvatarSerializer

class YandexLogin(SocialLoginView):
    adapter_class = YandexAuth2Adapter

class GitHubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    
class TelegramLogin(SocialLoginView):
    adapter_class = LoginView
    
class RegisterView(APIView):
    @csrf_exempt
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(ObtainAuthToken):
    @csrf_exempt
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user_qs = User.objects.filter(username=username)
        if user_qs.count() == 0:
            return Response({"detail": "Пользователя с таким именем не существует"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return Response({"detail": "Успешная авторизация"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Неправильное имя пользователя или пароль"}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
       @csrf_exempt
       def post(self, request):
        logout(request)
        return Response({"detail": "Выход успешно выполнен"}, status=status.HTTP_200_OK)

class GenerateQRcode(APIView): 
    @csrf_exempt 
    def post(self, request):
        if request.method == 'POST':
            if request.data.get('username'):
                try:
                    user = User.objects.get(username=request.data.get('username'))
                except User.DoesNotExist:
                    return Response({'detail': 'Пользователя с таким именем не существует'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'Имя пользователя не указано'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                device = TOTPDevice.objects.get(user=user)
            except Exception:
                device = TOTPDevice.objects.create(user=user)
        
            uri = device.config_url
            img = qrcode.make(uri)
            buffered = io.BytesIO()
            img.save(buffered)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return Response({
                'qr_code': f"data:image/png;base64,{img_str}",
            })
        return Response({'detail': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

class VerifyOtp(APIView):   
    @csrf_exempt 
    def post(self, request):
        if request.method == 'POST':
            otp = request.data.get('otp')
            try:
                user = User.objects.get(username=request.data.get('username'))
            except User.DoesNotExist:
                return Response({'detail': 'Пользователя с таким именем не существует'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                device = TOTPDevice.objects.get(user=user)
                if device.verify_token(otp):
                    return Response({'detail': "Успешно"}, status=status.HTTP_200_OK)
                else:
                    return Response({'detail': 'Неправильный код'}, status=status.HTTP_400_BAD_REQUEST)
            except TOTPDevice.DoesNotExist:
                return Response({'detail': 'Для этого пользователя не установлено OTP'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'detail': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
class VerifyTelegram(APIView):
    @csrf_exempt 
    def post(self, request):
        if request.method == 'POST':
            telegramId = request.data.get('telegram_id')
            try:
                user = User.objects.get(telegram_id=telegramId)
                verificationCode = user.verification_code
                send_verification_code_to_telegram(telegramId, verificationCode)
                return Response({'detail': "Успешно"}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'detail': 'Пользователя с таким телеграмом не существует'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

class GetMarkdownPost(APIView):
    @csrf_exempt
    def post(self, request):
        if request.method == 'POST':
            try:
                post = Post.objects.get(title=request.data.get('title'))
                images = markdown_find_images(post.description)
                images_str = {}
                for image in images:
                    image_src = str(settings.BASE_DIR) + image
                    with open(image_src, 'rb') as opened_image:
                        image_str = base64.b64encode(opened_image.read()).decode()
                        images_str[image] = image_str

                template = loader.get_template('markdown.html')
                context = {"post":post}
                return Response(data={"images":images_str, "tempalte":template.render(context)}, status=status.HTTP_200_OK)
            except Post.DoesNotExist:
                return Response({'detail': 'Поста с таким заголовком не существует'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
def markdown_uploader(request):
    if request.method == 'POST':
        if 'markdown-image-upload' in request.FILES:
            image = request.FILES['markdown-image-upload']
            image_types = [
                'image/png', 'image/jpg',
                'image/jpeg', 'image/pjpeg', 'image/gif'
            ]
            if image.content_type not in image_types:
                data = json.dumps({
                    'status': 405,
                    'error': _('Bad image format.')
                }, cls=LazyEncoder)
                return HttpResponse(
                    data, content_type='application/json', status=405)

            if image.size > settings.MAX_IMAGE_UPLOAD_SIZE:
                to_MB = settings.MAX_IMAGE_UPLOAD_SIZE / (1024 * 1024)
                data = json.dumps({
                    'status': 405,
                    'error': _('Maximum image file is %(size)s MB.') % {'size': to_MB}
                }, cls=LazyEncoder)
                return HttpResponse(
                    data, content_type='application/json', status=405)

            img_uuid = "{0}-{1}".format(uuid.uuid4().hex[:10], image.name.replace(' ', '-'))
            tmp_file = os.path.join(settings.MARTOR_UPLOAD_PATH, img_uuid)
            def_path = default_storage.save(tmp_file, ContentFile(image.read()))
            img_url = os.path.join(settings.MEDIA_URL, def_path)

            data = json.dumps({
                'status': 200,
                'link': img_url,
                'name': image.name
            })
            return HttpResponse(data, content_type='application/json')
        return HttpResponse(_('Invalid request!'))
    return HttpResponse(_('Invalid request!'))
       
def init(request):
    return render(
            request,
            'empty.html'
        )

def home(request):
    return render(
            request,
            'home.html',
    )

def courses(request):
    return render(
            request,
            'courses.html',
    )

def training(request):
    return render(
            request,
            'training.html',
    )
def resources(request):
    return render(
            request,
            'resources.html',
    )

def resources__articles(request):
    return render(
            request,
            'resources__articles.html',
    )
def resources__articles_fishings(request):
    return render(
            request,
            'resources__articles_fishings.html',
    )
def custom_articles(request):
    return render(
            request,
            'custom_articles.html',
    )
def add_article(request):
    return render(
            request,
            'add_article.html',
    )
def edit_article(request):
    return render(
            request,
            'edit_article.html',
    )
def tests(request):
    return render(
            request,
            'tests.html',
    )
def personal_account(request):
    return render(
            request,
            'personal_account.html',
    )
def create_test(request):
    return render(
            request,
            'create_test.html',
    )
def take_test(request):
    return render(
            request,
            'take_test.html',
    )

class TestGetPost(APIView):
    @requires_csrf_token
    def get(self, request):
        test = get_or_none(Test, title=request.data.get('title'))
        if test is None:
            return Response({'detail': 'Теста с таким заголовком не существует'}, status=status.HTTP_400_BAD_REQUEST)
        questionSet = Question.objects.filter(test_id=test.id).order_by("?")
        questions = {}
        for question in questionSet:
            answersSet = Answer.objects.filter(question_id=question)
            answers = {}
            for answer in answersSet:
                answers[answer.id] = answer.answer_text
            questions[question.id] = [question.question_text, answers]
        return Response(data={"title":test.title, "description":test.description, "createdAt":test.created_at, "questions":questions},
                            status=status.HTTP_200_OK)
    @requires_csrf_token
    def post(self, request):
        serializer = TestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        title = serializer.validated_data['title']
        description = serializer.validated_data['description']

        serializer.save(request.data)
        return Response(data={"title":title, "description":description, "createdAt":datetime.date.today()}, status=status.HTTP_200_OK)

class TestQuestionsAnswersPost(APIView):
    @requires_csrf_token
    def post(self, request):
        test = get_or_none(Test, title=request.data.get('title'))
        if test is None:
            return Response({'detail': 'Теста с таким заголовком не существует'}, status=status.HTTP_400_BAD_REQUEST)
        questions = request.data.get("questions")
        for question in questions:
            m_question = Question.objects.create(test_id=test.id, question_text=question[0], created_at=datetime.date.today())
            m_question.save()
            answers = question[1]
            for answer in answers:
                m_answer = Answer.objects.create(question_id=m_question, answer_text=answer[0])
                m_answer.save()
                if answer[1] == True:
                    m_correct_answer = CorrectAnswer.objects.create(question_id=m_question, answer_id=m_answer)
                    m_correct_answer.save()
        return Response(data={"detail":"Тест успешно создан"}, status=status.HTTP_200_OK)

class TestCheckAnswers(APIView):
    @requires_csrf_token
    def post(self, request):
        test = get_or_none(Test, title=request.data.get('title'))
        if test is None:
            return Response({'detail': 'Теста с таким заголовком не существует'}, status=status.HTTP_400_BAD_REQUEST)
        questions = request.data.get('questions')
        result = {}
        for question in questions:
            m_question = Question.objects.get(test_id=test.id, id=question)
            flag = True
            for answer in questions.get(question):
                m_answer = Answer.objects.get(id=answer)
                if not CorrectAnswer.objects.filter(question_id=m_question, answer_id=m_answer):
                    result[question] = False
                    flag = False
                    break
            if flag:
                result[question] = True

        return Response({"result":result}, status=status.HTTP_200_OK)   