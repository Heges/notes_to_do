from django.contrib.auth import login
from django.contrib.auth.models import User, Group
from django.views.generic import TemplateView
from rest_framework import viewsets, routers, permissions
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView, ListCreateAPIView, \
    RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from main.models import Profile, Category, Notes, Tags
from main.seriliazers import RegistrationUsersSerializer, ProfileUserSerializer, CategoriesSerializer, \
    NotesSerializer, TagsSerializer, NotesUpdateSerializer


class TagsListAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TagsSerializer

    def get_queryset(self):
        return Tags.objects.all()


class TagsAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TagsSerializer

    def get_object(self):
        return Tags.objects.filter(id=self.kwargs['tags_pk']).first()


class NotesListAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return NotesSerializer if self.request.method == 'GET' else NotesUpdateSerializer

    def get_queryset(self):
        return Notes.objects.filter(category__user=self.request.user, category_id=self.kwargs['category_pk'])

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = NotesSerializer(serializer.instance)
        return Response(serializer.data, status=201)


class NoteAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return NotesSerializer if self.request.method == 'GET' else NotesUpdateSerializer

    def get_queryset(self):
        return Notes.objects.filter(category__user=self.request.user, category_id=self.kwargs['category_pk'])

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(NotesSerializer(serializer.instance).data)


class CategoriesListAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategoriesSerializer

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class CategoryAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategoriesSerializer

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class ProfileUser(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileUserSerializer

    def get_object(self):
        return self.request.user


# class ProfileUpdateUser(RetrieveUpdateAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = ProfileUserSerializer
#
#     def get_object(self):
#         return self.request.user
#
#     def get_serializer_class(self):
#         return ProfileUserSerializer if self.request.method == 'GET' else ProfileUserUpdateSerializer
#
#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)
#
#         if getattr(instance, '_prefetched_objects_cache', None):
#             # If 'prefetch_related' has been applied to a queryset, we need to
#             # forcibly invalidate the prefetch cache on the instance.
#             instance._prefetched_objects_cache = {}
#
#         return Response(NotesSerializer(serializer.instance).data)


class RegistrationUsersApi(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationUsersSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            new_user = serializer.save()
            data['response'] = 'Ура ты создал нового персонажа, героя, человека, или не создал?'
            data['email'] = new_user.email
            data['username'] = new_user.username
            data['password'] = new_user.password
            # data['token'] = Profile.get_tokens_for_user(new_user)
        else:
            serializer.errors
        return Response(data)
