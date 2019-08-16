from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Profile(models.Model):

    user = models.OneToOneField(User, related_name='user_profile', on_delete=models.CASCADE)
    nickname = models.CharField(max_length=20, null=True, default=None, verbose_name='昵称')
    profile = models.TextField(default='暂无介绍', verbose_name='个人简介')
    motto = models.CharField(max_length=100, default='正在思考中......', verbose_name='座右铭')

    class Meta:
        verbose_name = "个人信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.username