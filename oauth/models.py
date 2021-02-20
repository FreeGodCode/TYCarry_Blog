from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
import datetime

# Create your models here.
from django.utils.translation import gettext_lazy


class OAuthUser(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='用户', blank=True, null=True, on_delete=models.CASCADE)
    openid = models.CharField(max_length=50)
    nickname = models.CharField(verbose_name='昵称', max_length=50)
    token = models.CharField(max_length=150, null=True, blank=True)
    picture = models.CharField(max_length=350, blank=True, null=True)
    type = models.CharField(blank=False, null=False, max_length=50)
    email = models.CharField(max_length=50, null=True, blank=True)
    matedata = models.TextField(null=True, blank=True)
    created_time = models.DateTimeField(verbose_name='创建时间', default=datetime.datetime.now)
    last_modify_time = models.DateTimeField(verbose_name='修改时间', default=datetime.datetime.now)

    def __str__(self):
        return self.nickname

    class Meta:
        db_table = 'db_oauth_user'
        ordering = ['-created_time']
        verbose_name = 'oauth用户'
        verbose_name_plural = verbose_name


class OAuthConfig(models.Model):
    TYPE = (
        ('weibo', '微博'),
        ('google', '谷歌'),
        ('github', 'GitHub'),
        ('facebook', 'FaceBook'),
        ('qq', 'QQ'),
    )
    type = models.CharField(verbose_name='类型', max_length=10, choices=TYPE, default='a')
    appkey = models.CharField(verbose_name='AppKey', max_length=200)
    appsecret = models.CharField(verbose_name='AppSecret', max_length=200)
    callback_url = models.CharField(verbose_name='回调地址', max_length=200, blank=False, default='http://www.baidu.com')
    is_enable = models.BooleanField(verbose_name='是否显示', default=True, blank=False, null=False)
    created_time = models.DateTimeField(verbose_name='创建时间', default=datetime.datetime.now)
    last_mod_time = models.DateTimeField(verbose_name='修改时间', default=datetime.datetime.now)

    def clean(self):
        if OAuthConfig.objects.filter(type=self.type).exclude(id=self.id).count():
            raise ValidationError(gettext_lazy(self.type + '已经存在'))

    def __str__(self):
        return self.type

    class Meta:
        db_table = 'db_oauth_config'
        ordering = ['-created_time']
        verbose_name = 'oauth配置'
        verbose_name_plural = verbose_name
