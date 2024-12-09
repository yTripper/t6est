from asgiref.sync import sync_to_async
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import requires_csrf_token, csrf_exempt
from django.conf import settings

import requests
import json

from cyberpolygonApp.models import User, UserDoingTask, Task
from cyberpolygonApp.utils import get_or_none

VAGRANT_API_KEY = settings.VAGRANT_API_KEY
LOCALHOST =  settings.LOCALHOST


class VagrantStartTask(APIView):
    def post(self, request):
        task = request.data.get('task')
        username = request.data.get('username')
        print(username)

        url = LOCALHOST + f"vms/manage_vm/start/?vm_name={task}&api_key={VAGRANT_API_KEY}"

        user = get_or_none(User, username=username)

        if user is None:
            return Response({'detail': 'Пользователь не найден'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            vagrant_response = requests.get(url)
            print(vagrant_response.text)

            vagrant_response_data = vagrant_response.json()
            flag = vagrant_response_data.get("Flag")
            vagrant_password = vagrant_response_data.get("Password")
            task_status = get_or_none(UserDoingTask, task=task, user=user)

            if task_status is None:
                UserDoingTask.objects.create(
                    task=task,
                    user=user,
                    flag=flag,
                    vagrant_password=vagrant_password,
                    is_active=True
                )
            else:
                task_status.flag = flag
                task_status.vagrant_password = vagrant_password
                task_status.is_active = True
                task_status.save()

            return Response({"detail": "Виртуальная машина запущена и информация сохранена."},
                            status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': f"Ошибка с виртуальной машиной: {str(e)}"},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)


class VagrantStopTask(APIView):
    @requires_csrf_token
    async def post(self, request):
        if request.method == 'POST':
            task_title = request.data.get('task')
            username = request.data.get('username')

            task = await sync_to_async(get_or_none)(Task, titfVagrantTaskRun=task_title)
            if task is None:
                return Response({'detail': 'Задания с таким заголовком не существует'}, status=status.HTTP_400_BAD_REQUEST)

            user = await sync_to_async(get_or_none)(User, username=username)
            if user is None:
                return Response({'detail': 'Пользователя с таким именем не существует'}, status=status.HTTP_400_BAD_REQUEST)

            task_status = await sync_to_async(get_or_none)(UserDoingTask, task=task, user=user)

            url = LOCALHOST + f"vms/manage_vm/stop/?vm_name={task.title}&api_key={VAGRANT_API_KEY}"
            try:
                response = await sync_to_async(requests.get)(url)
                if json.loads(response.text).get("Stop") == "OK." and task_status is not None:
                    task_status.is_active = False
                    await sync_to_async(task_status.save)()
                    return Response(data={"detail": "Виртуальная машина остановлена"}, status=status.HTTP_200_OK)
                else:
                    return Response({'detail': 'Ошибка с виртуальной машиной'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            except Exception:
                return Response({'detail': 'Ошибка с виртуальной машиной'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({'detail': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class VagrantReloadTask(APIView):
    @requires_csrf_token
    async def post(self, request):
        if request.method == 'POST':
            task_title = request.data.get('task')
            username = request.data.get('username')

            task = await sync_to_async(get_or_none)(Task, title=task_title)
            if task is None:
                return Response({'detail': 'Задания с таким заголовком не существует'}, status=status.HTTP_400_BAD_REQUEST)

            user = await sync_to_async(get_or_none)(User, username=username)
            if user is None:
                return Response({'detail': 'Пользователя с таким именем не существует'}, status=status.HTTP_400_BAD_REQUEST)

            task_status = await sync_to_async(get_or_none)(UserDoingTask, task=task, user=user)
            if task_status is None:
                return Response({'detail': 'Задание для этого пользователя не запущено'}, status=status.HTTP_400_BAD_REQUEST)

            url = LOCALHOST + f"vms/manage_vm/reload/?vm_name={task.title}&api_key={VAGRANT_API_KEY}"
            try:
                response = await sync_to_async(requests.get)(url)
                if json.loads(response.text).get("Reload") == "OK":
                    return Response(data={"detail": "Виртуальная машина перезагружена"}, status=status.HTTP_200_OK)
                else:
                    raise Exception
            except Exception:
                return Response({'detail': 'Ошибка с виртуальной машиной'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({'detail': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TaskCheckFlag(APIView):
    @requires_csrf_token
    async def post(self, request):
        if request.method == 'POST':
            task_title = request.data.get('task')
            username = request.data.get('username')
            flag = request.data.get('flag')

            task = await sync_to_async(get_or_none)(Task, title=task_title)
            if task is None:
                return Response({'detail': 'Задания с таким заголовком не существует'}, status=status.HTTP_400_BAD_REQUEST)

            user = await sync_to_async(get_or_none)(User, username=username)
            if user is None:
                return Response({'detail': 'Пользователя с таким именем не существует'}, status=status.HTTP_400_BAD_REQUEST)

            user_doing_task = await sync_to_async(get_or_none)(UserDoingTask, task=task, user=user)
            if user_doing_task is None or not user_doing_task.is_active:
                return Response({'detail': 'Задание не запущено'}, status=status.HTTP_400_BAD_REQUEST)

            if user_doing_task.flag == flag:
                return Response(data={"detail": "Флаг совпадает"}, status=status.HTTP_200_OK)
            return Response(data={"detail": "Флаг не совпадает"}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        return Response({'detail': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)