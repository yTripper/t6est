from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token
from rest_framework.views import APIView
from asgiref.sync import sync_to_async
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status

import datetime

from cyberpolygonApp.utils import markdown_find_images, get_or_none
from cyberpolygonApp.models import *
from .serializers import *

class TestGetPost(APIView):
    @requires_csrf_token
    async def get(self, request):
        title = request.data.get('title')
        test = await sync_to_async(get_or_none)(Test, title=title)

        if test is None:
            return Response({'detail': 'Теста с таким заголовком не существует'}, status=status.HTTP_400_BAD_REQUEST)

        question_set = await sync_to_async(list)(Question.objects.filter(test_id=test.id).order_by("?"))
        questions = {}

        for question in question_set:
            answers_set = await sync_to_async(list)(Answer.objects.filter(question_id=question))
            answers = {answer.id: answer.answer_text for answer in answers_set}
            questions[question.id] = [question.question_text, answers]

        return Response(data={
            "title": test.title,
            "description": test.description,
            "createdAt": test.created_at,
            "questions": questions
        }, status=status.HTTP_200_OK)

    @requires_csrf_token
    async def post(self, request):
        serializer = TestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        title = serializer.validated_data['title']
        description = serializer.validated_data['description']

        await sync_to_async(serializer.save)(request.data)
        return Response(data={
            "title": title,
            "description": description,
            "createdAt": datetime.date.today()
        }, status=status.HTTP_200_OK)


class TestQuestionsAnswersPost(APIView):
    @requires_csrf_token
    async def post(self, request):
        title = request.data.get('title')
        test = await sync_to_async(get_or_none)(Test, title=title)

        if test is None:
            return Response({'detail': 'Теста с таким заголовком не существует'}, status=status.HTTP_400_BAD_REQUEST)

        questions = request.data.get("questions")
        for question in questions:
            m_question = await sync_to_async(Question.objects.create)(
                test_id=test.id,
                question_text=question[0],
                created_at=datetime.date.today()
            )
            answers = question[1]
            for answer in answers:
                m_answer = await sync_to_async(Answer.objects.create)(
                    question_id=m_question,
                    answer_text=answer[0]
                )
                if answer[1] is True:
                    await sync_to_async(CorrectAnswer.objects.create)(
                        question_id=m_question,
                        answer_id=m_answer
                    )

        return Response(data={"detail": "Тест успешно создан"}, status=status.HTTP_200_OK)


class TestCheckAnswers(APIView):
    @requires_csrf_token
    async def post(self, request):
        title = request.data.get('title')
        test = await sync_to_async(get_or_none)(Test, title=title)

        if test is None:
            return Response({'detail': 'Теста с таким заголовком не существует'}, status=status.HTTP_400_BAD_REQUEST)

        questions = request.data.get('questions')
        result = {}

        for question_id, answer_ids in questions.items():
            m_question = await sync_to_async(Question.objects.get)(test_id=test.id, id=question_id)
            flag = True

            for answer_id in answer_ids:
                m_answer = await sync_to_async(Answer.objects.get)(id=answer_id)
                is_correct = await sync_to_async(CorrectAnswer.objects.filter)(
                    question_id=m_question, answer_id=m_answer
                ).exists()

                if not is_correct:
                    result[question_id] = False
                    flag = False
                    break

            if flag:
                result[question_id] = True

        return Response({"result": result}, status=status.HTTP_200_OK)