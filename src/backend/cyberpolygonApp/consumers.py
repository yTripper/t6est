import paramiko
import json
from .utils import get_or_none
from .models import Task, User, UserDoingTask
from channels.generic.websocket import AsyncWebsocketConsumer
LOCALHOST = "127.0.0.1:2222"

class SSHConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        self.channel.close()
        self.ssh_client.close()

    async def receive(self, text_data):
        data = json.loads(text_data)
        if "info" in data:
            await self.vagrantConnect(data['info'])
        command = text_data.strip()
        if command:
            self.channel.send(command)
            while True:
                if self.channel.recv_ready():
                    output = self.channel.recv(1024).decode('utf-8')
                    await self.send(output)
                    break

    async def vagrantConnect(self, info):
        task = get_or_none(Task, title=info["title"])
        if task is None:
            await self.send("Задания с таким заголовком не существует")
            await self.disconnect(self)
        user = get_or_none(User, username=info["username"])
        if user is None:
            await self.send("Пользователя с таким именем не существует")
            await self.disconnect(self)
        userDoingTask = get_or_none(UserDoingTask, task=task, user=user)
        if userDoingTask is not None and userDoingTask.is_active == True:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(LOCALHOST, username=task.title, password=userDoingTask.vagrant_password)

            self.channel = self.ssh_client.invoke_shell()
            await self.send("Соединение установленно")
        else:
            await self.send("Задание не запущено")
            await self.disconnect(self)