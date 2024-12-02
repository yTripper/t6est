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
    def get(self, request):
        # Проверяем, есть ли параметр title
        title = request.GET.get('title')

        if title:
            # Если передан title, возвращаем конкретный тест
            test = get_or_none(Test, title=title)
            if test is None:
                return Response({'detail': 'Теста с таким заголовком не существует'}, status=status.HTTP_400_BAD_REQUEST)

            # Формируем список вопросов и ответов
            question_set = Question.objects.filter(test_id=test.id).order_by("?")
            questions = {}
            for question in question_set:
                answers_set = Answer.objects.filter(question_id=question)
                answers = [
                    {
                        "id": answer.id,
                        "text": answer.answer_text,
                        "is_correct": answer.is_correct  # Добавляем правильность ответа
                    }
                    for answer in answers_set
                ]
                questions[question.id] = {"question_text": question.question_text, "answers": answers}

            return Response(
                data={
                    "title": test.title,
                    "description": test.description,
                    "createdAt": test.created_at,
                    "questions": questions,
                },
                status=status.HTTP_200_OK,
            )
        else:
            # Если title не передан, возвращаем список всех тестов
            tests = Test.objects.all().order_by('-created_at')  # Сортируем по дате создания
            test_list = [
                {"title": test.title, "description": test.description, "createdAt": test.created_at}
                for test in tests
            ]
            return Response(data={"tests": test_list}, status=status.HTTP_200_OK)


    def post(self, request):
        serializer = TestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Создаем новый тест
        test = serializer.save()
        return Response(
            data={
                "title": test.title,
                "description": test.description,
                "createdAt": test.created_at,
            },
            status=status.HTTP_200_OK,
        )






from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Test, Question, Answer, CorrectAnswer
from .serializers import CorrectAnswerSerializer

class TestQuestionsAnswersPost(APIView):
    def post(self, request):
        # Проверяем существование теста
        test = get_or_none(Test, title=request.data.get('title'))
        if test is None:
            return Response({'detail': 'Теста с таким заголовком не существует'}, status=400)

        # Обрабатываем вопросы и ответы
        questions_data = request.data.get("questions", [])
        for question_data in questions_data:
            question = Question.objects.create(
                test_id=test,
                question_text=question_data['question_text'],
                created_at=datetime.date.today()
            )
            
            for answer_data in question_data.get('answers', []):
                answer = Answer.objects.create(
                    question_id=question,
                    answer_text=answer_data['answer_text'],
                    is_correct=answer_data.get('is_correct', False)
                )
                
                if answer_data.get('is_correct', False):
                    correct_answer_data = {
                        'question_id': question.id,
                        'answer_id': answer.id
                    }
                    serializer = CorrectAnswerSerializer(data=correct_answer_data)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        return Response(serializer.errors, status=400)

        return Response({'detail': 'Тест успешно создан'}, status=200)





from django.http import JsonResponse
from rest_framework import status

import logging
logger = logging.getLogger(__name__)

class TestCheckAnswers(APIView):
    def post(self, request):
        try:
            test_title = request.data.get('title')
            if not test_title:
                return Response({'detail': 'Заголовок теста не предоставлен'}, status=status.HTTP_400_BAD_REQUEST)

            # Получаем тест по заголовку
            test = get_or_none(Test, title=test_title)
            if test is None:
                return Response({'detail': 'Теста с таким заголовком не существует'}, status=status.HTTP_400_BAD_REQUEST)

            # Получаем ответы на вопросы
            questions = request.data.get('questions', {})
            if not isinstance(questions, dict) or not questions:
                return Response({'detail': 'Ответы на вопросы не предоставлены или имеют неверный формат'}, status=status.HTTP_400_BAD_REQUEST)

            # Загружаем вопросы и правильные ответы
            question_ids = questions.keys()
            db_questions = Question.objects.filter(test_id=test.id, id__in=question_ids).prefetch_related('correctanswer_set')
            question_map = {str(q.id): q for q in db_questions}

            result = {}
            for question_id, submitted_answers in questions.items():
                if not isinstance(submitted_answers, list):
                    result[question_id] = {
                        "correct": False,
                        "submitted_answers": submitted_answers,
                        "correct_answers": []
                    }
                    continue

                # Получаем вопрос из карты
                question = question_map.get(str(question_id))
                if not question:
                    result[question_id] = {
                        "correct": False,
                        "submitted_answers": submitted_answers,
                        "correct_answers": []
                    }
                    continue

                # Получаем правильные ответы
                correct_answers = set(
                    CorrectAnswer.objects.filter(question_id=question.id).values_list('answer_id', flat=True)
                )

                # Сравниваем правильные ответы с отправленными
                submitted_answers_set = set(map(int, submitted_answers))  # Преобразуем ответы в числа
                is_correct = correct_answers == submitted_answers_set

                # Формируем результат
                result[question_id] = {
                    "correct": is_correct,
                    "submitted_answers": list(submitted_answers_set),
                    "correct_answers": list(correct_answers)
                }

            return Response({"result": result}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Произошла ошибка: {str(e)}", exc_info=True)
            return JsonResponse({"detail": "Внутренняя ошибка сервера"}, status=500)
