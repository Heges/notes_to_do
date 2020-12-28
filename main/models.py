from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


class Category(models.Model):
    user = models.ForeignKey(get_user_model(), verbose_name='Пользователь', on_delete=models.CASCADE,
                             related_name='categories')
    title = models.CharField('Название', max_length=50)


class Tags(models.Model):
    title = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.title


class Notes(models.Model):
    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE,
                                 related_name='notes')
    text = models.TextField('Text', blank=True)
    tags = models.ManyToManyField(Tags, verbose_name='Тэги', related_name='notes', blank=True)

    def __str__(self):
        return self.text[:100]


class Profile(models.Model):
    MONTH_CHOICES = (
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    )
    SEX_CHOICES = (
        ('1', 'Male'),
        ('2', 'Female'),
        ('3', 'Other'),
        ('4', 'Argonianin'),
        ('5', 'Kajit')
    )
    # REGION = (
    #     ('RU', '+7'),
    #     ('US', '+1'),
    # )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    info = models.CharField(max_length=30, null=True, blank=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    second_name = models.CharField(max_length=30, null=True, blank=True)
    daybirth = models.DateField(default=None)
    sex = models.CharField(max_length=2, choices=SEX_CHOICES, default='5')
    image = models.FileField(upload_to='uploads/', null=True, blank=True)
    number_phone = models.CharField(max_length=11, null=True, blank=True)

    def __str__(self):
        return self.user.username
