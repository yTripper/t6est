from django.urls import path, include, re_path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create_test/', views.create_test, name='create_test'),
    path('take_test/', views.take_test, name='take_test'),
    path('courses/', views.courses, name='courses'),
    path('training/', views.training, name='training'),
    path('resources/', views.resources, name='resources'),
    path('personal_account/', views.personal_account, name='personal_account'),
    path('resources/resources__articles', views.resources__articles, name='resources__articles'),
    path('resources/custom_articles', views.custom_articles, name='custom_articles'),
    path('resources/tests', views.tests, name='tests'),
    path('resources/custom_articles/add_article', views.add_article, name='add_article'),
    path('resources/custom_articles/edit_article', views.edit_article, name='edit_article'),
    path('resources/resources__articles/resources__articles_fishings', views.resources__articles_fishings, name='resources__articles_fishings'),
    path("accounts/", include("allauth_2fa.urls")),
    path("accounts/", include("allauth.urls")),
    path('martor/', include('martor.urls')),
    path('api/user', views.UserListCreate.as_view()),
    
    re_path(r'^api/user/(?P<pk>[0-9]+)/$', views.UserRetrieveUpdateDestroy.as_view() ),

    path('api/categories/', views.CategoryListCreate.as_view()),
    re_path(r'^api/categories/(?P<pk>[0-9]+)/$', views.CategoryRetrieveUpdateDestroy.as_view() ),

    path('api/tasks/', views.TaskListCreate.as_view()),
    re_path(r'^api/tasks/(?P<pk>[0-9]+)/$', views.TaskRetrieveUpdateDestroy.as_view() ),

    path('api/comments/', views.CommentsListCreate.as_view()),
    re_path(r'^api/comments/(?P<pk>[0-9]+)/$', views.CommentsRetrieveUpdateDestroy.as_view() ),

    path('api/avatars/', views.UserAvatarListCreate.as_view()),
    re_path(r'^api/avatars/(?P<pk>[0-9]+)/$', views.UserAvatarRetrieveUpdateDestroy.as_view() ),

    #api auth
    path('api/auth/yandex/', views.YandexLogin.as_view(), name='yandex_login_api'),
    path('api/auth/github/', views.GitHubLogin.as_view(), name='github_login_api'),
    path('api/auth/telegram/', views.TelegramLogin.as_view(), name='telegram_login_api'),
    path('api/auth/signup/', views.RegisterView.as_view(), name='registration'),
    path('api/auth/login/', views.LoginView.as_view(), name='login'),
    path('api/auth/logout/', views.LogoutView.as_view(), name='logout'),

    #otp
    path('api/generate_qr/', views.GenerateQRcode.as_view(), name='generate_qr_code'),
    path('api/verify_otp/', views.VerifyOtp.as_view(), name='verify_otp'),
    path('api/verify_telegram/', views.VerifyTelegram.as_view(), name='verify_telegram'),

    #markdown
    path('api/get_markdown_post', views.GetMarkdownPost.as_view(), name='get_markdown_post'),
    path('api/markdown_uploader/', views.markdown_uploader, name='markdown_uploader_page'),

    #tests
    path('api/tests/', views.TestGetPost.as_view(), name="get_post_test"),
    path('api/tests/content/', views.TestQuestionsAnswersPost.as_view(), name="test_questions_answers_post" ),
    path('api/tests/check/', views.TestCheckAnswers.as_view(), name="test_check_answers"),
]
