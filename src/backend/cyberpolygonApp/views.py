from asgiref.sync import sync_to_async
from django.shortcuts import render
from rest_framework.views import APIView
from .utils import markdown_find_images, get_or_none
from rest_framework.response import Response
from django.http import HttpResponse
from django.conf import settings
from rest_framework import status
from django.views.decorators.csrf import requires_csrf_token, csrf_exempt
from martor.utils import LazyEncoder
from django.template import loader
import datetime
from .models import Test, Question, Answer, CorrectAnswer
from .serializers import *
import base64
import json

from .forms import *

# Временно
from asgiref.sync import sync_to_async
from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import authenticate, login, logout
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.yandex.views import YandexAuth2Adapter
from allauth.socialaccount.providers.telegram.views import LoginView
from cyberpolygonApp.utils import get_or_none
from django_otp.plugins.otp_totp.models import TOTPDevice
from .serializers import *

import qrcode
import io
import base64

class GetMarkdownPost(APIView):
    @requires_csrf_token
    async def post(self, request, aiofiles=None):
        title = request.data.get('title')
        post = await sync_to_async(get_or_none)(Post, title=title)

        if post is None:
            return Response({'detail': 'Поста с таким заголовком не существует'}, status=status.HTTP_400_BAD_REQUEST)

        images = markdown_find_images(post.description)
        images_str = {}
        for image in images:
            image_src = str(settings.BASE_DIR) + image
            async with aiofiles.open(image_src, 'rb') as f:
                content = await f.read()
            images_str[image] = base64.b64encode(content).decode()

        template = loader.get_template('markdown.html')
        context = {"post": post}
        rendered_template = await sync_to_async(template.render)(context)

        return Response(data={"images": images_str, "template": rendered_template}, status=status.HTTP_200_OK)

    
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
                    'error': 'Bad image format.'
                }, cls=LazyEncoder)
                return HttpResponse(
                    data, content_type='application/json', status=405)

            if image.size > settings.MAX_IMAGE_UPLOAD_SIZE:
                to_MB = settings.MAX_IMAGE_UPLOAD_SIZE / (1024 * 1024)
                data = json.dumps({
                    'status': 405,
                    'error': ('Maximum image file is %(size)s MB.') % {'size': to_MB}
                }, cls=LazyEncoder)
                return HttpResponse(
                    data, content_type='application/json', status=405)

            img_url = upload_image_info(image)["img_url"]

            data = json.dumps({
                'status': 200,
                'link': img_url,
                'name': image.name
            })
            return HttpResponse(data, content_type='application/json')
        return HttpResponse('Invalid request!')
    return HttpResponse('Invalid request!')


async def init(request):
    return render(
        request,
        'empty.html'
    )

async def home(request):
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



# Временно
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
    
class RegisterView(APIView):
    @csrf_exempt
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)