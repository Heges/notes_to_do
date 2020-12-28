from django.urls import path, include
from rest_framework import routers

from . import views
from .views import CategoriesListAPIView, CategoryAPIView, NotesListAPIView, NoteAPIView, \
    TagsListAPIView, TagsAPIView

urlpatterns = [
    path('registration/', views.RegistrationUsersApi.as_view(), name='registration'),
    path('profile/', views.ProfileUser.as_view(), name='profile'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('category/', CategoriesListAPIView.as_view()),
    path('category/<pk>', CategoryAPIView.as_view()),
    path('category/<category_pk>/notes', NotesListAPIView.as_view()),
    path('category/<category_pk>/notes/<pk>', NoteAPIView.as_view()),
    path('tags/', TagsListAPIView.as_view()),
    path('tags/<tags_pk>/', TagsAPIView.as_view()),

]
