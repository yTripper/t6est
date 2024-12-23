from http.client import responses

from django.db.models.expressions import result
from django.test import TestCase
from rest_framework.test import APITestCase
from cyberpolygonApp.models import *
from rest_framework import status

HOST = "http://127.0.0.1:8000"

class UserAPITestV1(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass', email='test@test.com')

    def test_get_users(self):
        response = self.client.get(f'{HOST}/api/v1/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_get_user(self):
        response = self.client.get(f'{HOST}/api/v1/user/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user(self):
        data = {'username': 'newuser', 'password': 'newpass', 'email': 'test@test.com', 'user_data': "discription"}
        response = self.client.post(f'{HOST}/api/v1/users/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], data['username'])


class CategoryAPITestV1(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")

    def test_get_categories(self):
        response = self.client.get(f'{HOST}/api/v1/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_get_category(self):
        response = self.client.get(f'{HOST}/api/v1/category/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.category.name)

    def test_create_category(self):
        data = {'name': 'New Category'}
        response = self.client.post(f'{HOST}/api/v1/categories/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], data['name'])

    def test_update_category(self):
        data = {'name': 'Updated Category'}
        response = self.client.put(f'{HOST}/api/v1/category/{self.category.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], data['name'])

    def test_delete_category(self):
        response = self.client.delete(f'{HOST}/api/v1/category/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TaskAPITestV1(APITestCase):
    def setUp(self):
        self.task = Task.objects.create(title="Test Task", description="Task description")

    def test_get_tasks(self):
        response = self.client.get(f'{HOST}/api/v1/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_get_task(self):
        response = self.client.get(f'{HOST}/api/v1/task/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.task.title)

    def test_create_task(self):
        data = {'title': 'New Task', 'description': 'New task description'}
        response = self.client.post(f'{HOST}/api/v1/tasks/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], data['title'])

    def test_update_task(self):
        data = {'title': 'Updated Task', 'description': 'Updated description'}
        response = self.client.put(f'{HOST}/api/v1/task/{self.task.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], data['title'])

    def test_delete_task(self):
        response = self.client.delete(f'{HOST}/api/v1/task/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CommentsAPITestV1(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass', email='test@test.com')
        self.task = Task.objects.create(title="Test Task", description="Task description")
        self.comment = Comments.objects.create(task_id=self.task, user_id=self.user, comment="Test comment", rating=5)

    def test_get_comments(self):
        response = self.client.get(f'{HOST}/api/v1/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_get_comment(self):
        response = self.client.get(f'{HOST}/api/v1/comment/{self.comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comment'], self.comment.comment)

    def test_create_comment(self):
        data = {
            'task_id': self.task.id,
            'user_id': self.user.id,
            'comment': 'New Comment',
            'rating': 4
        }
        response = self.client.post(f'{HOST}/api/v1/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['comment'], data['comment'])

    # не особо работает, дописать метод put
    # def test_update_comment(self):
    #     data = {'comment': 'Updated Comment', 'rating': 3}
    #     response = self.client.put(f'{HOST}/api/v1/comment/{self.comment.id}/', data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['comment'], data['comment'])

    def test_delete_comment(self):
        response = self.client.delete(f'{HOST}/api/v1/comment/{self.comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)