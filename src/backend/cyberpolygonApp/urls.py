from django.urls import path, include, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ссылки app
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

    # временно для проверки работы
    path('api/tests/', views.TestGetPost.as_view(), name="get_post_test"),
    path('api/tests/content/', views.TestQuestionsAnswersPost.as_view(), name="test_questions_answers_post" ),
    path('api/tests/check/', views.TestCheckAnswers.as_view(), name="test_check_answers"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
