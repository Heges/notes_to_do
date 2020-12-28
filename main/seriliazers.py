import email

import data as data
from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth.models import User, Group

from main.models import Profile, Category, Notes, Tags


class ProfileUserSerializer(serializers.ModelSerializer):
    info = serializers.CharField(source='profile.info')
    first_name = serializers.CharField(source='profile.first_name')
    second_name = serializers.CharField(source='profile.second_name')
    daybirth = serializers.DateField(source='profile.daybirth')
    sex = serializers.CharField(source='profile.sex')
    number_phone = serializers.CharField(source='profile.number_phone')

    class Meta:
        model = User
        fields = ['info', 'first_name', 'second_name', 'daybirth', 'sex', 'number_phone']

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        profile, _ = Profile.objects.get_or_create(info=profile_data['info'],
                                                   first_name=profile_data['first_name'],
                                                   second_name=profile_data['second_name'],
                                                   daybirth=profile_data['daybirth'],
                                                   sex=profile_data['sex'],
                                                   number_phone=profile_data['number_phone']
                                                   )
        profile.save()
        return profile

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        obj = super(ProfileUserSerializer, self).update(instance, validated_data)
        if profile_data:
            if hasattr(instance, 'profile'):
                profile = instance.profile
                profile.info = profile_data.get('info')
                profile.first_name = profile_data.get('first_name')
                profile.second_name = profile_data.get('second_name')
                profile.daybirth = profile_data.get('daybirth')
                profile.sex = profile_data.get('sex')
                profile.number_phone = profile_data.get('number_phone')
                profile.save()
            else:
                Profile(user=instance)
        return obj


class RegistrationUsersSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        user = User(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password': 'Password must match'})
        user.set_password(password)
        user.save()
        profile = Profile.objects.create(user=user,
                                         info='',
                                         first_name='',
                                         second_name='',
                                         daybirth="2001-12-28",
                                         sex='5',
                                         number_phone=''
                                         )
        profile.save()
        return user


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title')

    def create(self, validated_data):
        category, _ = Category.objects.get_or_create(user=self.context['request'].user, title=validated_data['title'])
        return category


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ('id', 'title',)

    def create(self, validated_data):
        t_tags = validated_data.pop('title')
        for tags_count in range(len(t_tags)):
            if t_tags.startswith('#'):
                tags, _ = Tags.objects.get_or_create(title=t_tags)
            else:
                t_tags = '#' + t_tags[0:]
                tags, _ = Tags.objects.get_or_create(title=t_tags)
        return tags


class NotesSerializer(serializers.ModelSerializer):
    category = CategoriesSerializer(read_only=True)
    tags = TagsSerializer(many=True)

    class Meta:
        model = Notes
        fields = ('id', 'category', 'text', 'tags')


class StringListField(serializers.ListField):
    child = serializers.CharField()


class NotesUpdateSerializer(NotesSerializer):
    tags = StringListField()

    # пихаем это в validated_data
    def validate(self, attrs):
        attrs['category_id'] = self.context['view'].kwargs['category_pk']
        return attrs

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        text = validated_data.pop('text')
        note = Notes.objects.create(**validated_data)
        s = ''.join(text)
        for i in s.split():
            if i.startswith('#'):
                tag, _ = Tags.objects.get_or_create(title=i)
                note.tags.add(tag)
                note.text = s
        for tag_title in tags:
            tag, _ = Tags.objects.get_or_create(title=tag_title)
            note.tags.add(tag)
        return note

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        text = validated_data.pop('text')
        obj = super().update(instance, validated_data)
        s = ''.join(text)
        for i in s.split():
            if i.startswith('#'):
                tag, _ = Tags.objects.get_or_create(title=i)
                obj.tags.add(tag)
        tags_ids = set(obj.tags.all().values_list('id', flat=True))
        adds_ids = set()
        for tag_title in tags:
            if tag_title.startswith('#'):
                tag, _ = Tags.objects.get_or_create(title=tag_title)
                adds_ids.add(tag.id)
                if tag.id not in tags_ids:
                    obj.tags.add(tag)
            else:
                tag_title = '#' + tag_title[0:]
                tag, _ = Tags.objects.get_or_create(title=tag_title)
                adds_ids.add(tag.id)
                if tag.id not in tags_ids:
                    obj.tags.add(tag)
        for tag_id in tags_ids - adds_ids:
            obj.tags.remove(tag_id)
        return obj
