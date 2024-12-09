from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user
        if sociallogin.account.provider == 'telegram':
            user.telegram_id = sociallogin.account.uid
            user.verification_code = get_random_string(length=6, allowed_chars='0123456789')

        if not user.username:
            Response({'error': 'Поле username пустое'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(username=user.username)
            sociallogin.connect(request, user)
            user.save()
        except User.DoesNotExist:
            Response({'error': 'Такого пользователя не существует'}, status=status.HTTP_400_BAD_REQUEST)