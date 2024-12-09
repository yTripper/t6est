from django.urls import path, include, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from . import views
from cyberpolygonAuth.views import YandexLogin, GitHubLogin, TelegramLogin, RegisterView, GenerateQRcode, VerifyOtp, VerifyTelegram, LoginView, LogoutView
from cyberpolygonTests.views import TestGetPost, TestQuestionsAnswersPost, TestCheckAnswers
from cyberpolygonApp.views import GetMarkdownPost, markdown_uploader
from cyberpolygonVM.views import VagrantStartTask, VagrantStopTask, VagrantReloadTask, TaskCheckFlag

urlpatterns = [
    # вход через соцсети
    path('v1/auth/yandex/', YandexLogin.as_view(), name='yandex_login_api'),
    path('v1/auth/github/', GitHubLogin.as_view(), name='github_login_api'),
    path('v1/auth/telegram/', TelegramLogin.as_view(), name='telegram_login_api'),
    path('v1/auth/signup/', RegisterView.as_view(), name='registration'),

    # otp
    path('v1/generate_qr/', GenerateQRcode.as_view(), name='generate_qr_code'),
    path('v1/verify_otp/', VerifyOtp.as_view(), name='verify_otp'),
    path('v1/verify_telegram/', VerifyTelegram.as_view(), name='verify_telegram'),

    # вход/выхол
    path('v1/auth/login/', LoginView.as_view(), name='login'),
    path('v1/auth/logout/', LogoutView.as_view(), name='logout'),

    # скачать схему документации
    path('schema/', SpectacularAPIView.as_view(), name='schema'),

    # документация api
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),

    # работа с бд
    # работа с пользователем
    path('v1/users/', views.UserListCreate.as_view()),

    re_path(r'^v1/user/(?P<pk>[0-9]+)/$', views.UserRetrieveUpdateDestroy.as_view()),

    # работа с запуском заданий на вм
    path('v1/tasks/', views.TaskListCreate.as_view()),
    re_path(r'^v1/task/(?P<pk>[0-9]+)/$', views.TaskRetrieveUpdateDestroy.as_view()),

    # комментарии
    path('v1/comments/', views.CommentsListCreate.as_view()),
    re_path(r'^v1/comment/(?P<pk>[0-9]+)/$', views.CommentsRetrieveUpdateDestroy.as_view()),

    # аватарки
    path('v1/avatars/', views.UserAvatarListCreate.as_view()),
    re_path(r'^v1/avatars/(?P<pk>[0-9]+)/$', views.UserAvatarRetrieveUpdateDestroy.as_view()),

    # категории заданий
    path('v1/categories/', views.CategoryListCreate.as_view()),
    re_path(r'^v1/category/(?P<pk>[0-9]+)/$', views.CategoryRetrieveUpdateDestroy.as_view()),

    # тесты
    path('v1/tests/', TestGetPost.as_view(), name="get_post_test"),
    path('v1/tests/content/', TestQuestionsAnswersPost.as_view(), name="test_questions_answers_post"),
    path('v1/tests/check/', TestCheckAnswers.as_view(), name="test_check_answers"),

    # markdown
    path('v1/get_markdown_post/', GetMarkdownPost.as_view(), name='get_markdown_post'),
    path('v1/markdown_uploader/', markdown_uploader, name='markdown_uploader_page'),

    # vagrant
    path('v1/vagrant/start', VagrantStartTask.as_view(), name="vagrant_start_task"),
    path('v1/vagrant/stop', VagrantStopTask.as_view(), name="vagrant_stop_task"),
    path('v1/vagrant/relaod', VagrantReloadTask.as_view(), name="vagrant_reload_task"),
    # Tasks
    path('v1/tasks/check_flag', TaskCheckFlag.as_view(), name="task_check_flag"),
]
