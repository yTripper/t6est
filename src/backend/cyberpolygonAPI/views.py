from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import *
from cyberpolygonApp.models import *
import requests

HOST = 'http://127.0.0.1:8001/'
VAGRANT_API_KEY = '314159265'

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



# class VagrantTaskRun(generics.RetrieveUpdateDestroyAPIView):
#     queryset = UserAvatar.objects.all()
#     serializer_class = UserAvatarSerializer
#
# class VagrantStartTask(APIView):
#     # def post(self, request):
#     #     task = get_or_none(Task, title=request.data.get('task'))
#     #     url = LOCALHOST + f"vms/manage_vm/start/?vm_name={task.title}&api_key={VAGRANT_API_KEY}"
#     #     try:
#     #         vagrant_response = requests.get(url)
#     #         print(vagrant_response.text)
#     #         flag = vagrant_response.text.get("Flag")
#     #         vagrant_password = vagrant_response.text.get("Password")
#     #     except Exception:
#     #         print("ошибка")
#     pass



# _________________________
