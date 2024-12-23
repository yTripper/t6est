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
from .verification import send_verification_code_to_telegram

import qrcode
import io
import base64


class YandexLogin(SocialLoginView):
    adapter_class = YandexAuth2Adapter


class GitHubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter


class TelegramLogin(SocialLoginView):
    adapter_class = LoginView


class RegisterView(APIView):
    @requires_csrf_token
    async def post(self, request):
        data = request.data
        serializer = RegistrationSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            await sync_to_async(serializer.save)(request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(ObtainAuthToken):
    @requires_csrf_token
    async def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user_qs = await sync_to_async(User.objects.filter)(username=username)
        if not user_qs.exists():
            return Response({"detail": "Пользователя не существует"}, status=status.HTTP_400_BAD_REQUEST)

        user = await sync_to_async(authenticate)(request, username=username, email=email, password=password)
        if user is not None:
            await sync_to_async(login)(request, user)
            return Response({"detail": "Успешная авторизация"}, status=status.HTTP_200_OK)
        return Response({"detail": "Неправильный пароль"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    @requires_csrf_token
    async def post(self, request):
        await sync_to_async(logout)(request)
        return Response({"detail": "Выход успешно выполнен"}, status=status.HTTP_200_OK)


class GenerateQRcode(APIView):
    @requires_csrf_token
    async def post(self, request):
        username = request.data.get('username')
        if not username:
            return Response({'detail': 'Имя пользователя не указано'}, status=status.HTTP_400_BAD_REQUEST)

        user = await sync_to_async(get_or_none)(User, username=username)
        if user is None:
            return Response({'detail': 'Пользователя с таким именем не существует'}, status=status.HTTP_400_BAD_REQUEST)

        device, created = await sync_to_async(TOTPDevice.objects.get_or_create)(user=user)

        uri = device.config_url
        qr_code = qrcode.make(uri)
        buffer = io.BytesIO()
        qr_code.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return Response({'qr_code': f"data:image/png;base64,{img_str}"}, status=status.HTTP_200_OK)

class VerifyOtp(APIView):
    @requires_csrf_token
    async def post(self, request):
        otp = request.data.get('otp')
        username = request.data.get('username')

        user = await sync_to_async(get_or_none)(User, username=username)
        if user is None:
            return Response({'detail': 'Пользователя с таким именем не существует'}, status=status.HTTP_400_BAD_REQUEST)

        device = await sync_to_async(get_or_none)(TOTPDevice, user=user)
        if device is None:
            return Response({'detail': 'Для этого пользователя не установлено OTP'}, status=status.HTTP_400_BAD_REQUEST)

        is_valid = await sync_to_async(device.verify_token)(otp)
        if is_valid:
            return Response({'detail': "Успешно"}, status=status.HTTP_200_OK)
        return Response({'detail': 'Неправильный код'}, status=status.HTTP_400_BAD_REQUEST)


class VerifyTelegram(APIView):
    @requires_csrf_token
    async def post(self, request):
        telegram_id = request.data.get('telegram_id')

        user = await sync_to_async(get_or_none)(User, telegramId=telegram_id)
        if user is None:
            return Response({'detail': 'Пользователя с таким телеграмом не существует'}, status=status.HTTP_400_BAD_REQUEST)

        verification_code = user.verification_code
        await sync_to_async(send_verification_code_to_telegram)(telegram_id, verification_code)
        return Response({'detail': "Успешно"}, status=status.HTTP_200_OK)
