from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.
from django.utils.timezone import now
from django.utils.translation import gettext_lazy


class AuthUser(models.Model):
    """验证表单模型类"""
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='用户', blank=True, null=True, on_delete=models.CASCADE)
    openid = models.CharField(max_length=50)
    nickname = models.CharField(max_length=50, verbose_name='昵称')
    token = models.CharField(max_length=150, null=True, blank=True)
    picture = models.CharField(max_length=350, blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    matedata = models.TextField(blank=True, null=True)
    created_time = models.DateTimeField(verbose_name='创建时间', default=now)
    last_modify_time = models.DateTimeField(default=now, verbose_name='修改时间')

    def __str__(self):
        return self.nickname

    class Meta:
        db_table = 'db_auth_user'
        verbose_name = 'auth用户'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']


class AuthConfig(models.Model):
    """用户配置 模型类"""
    TYPE = (
        ('weibo', '微博'),
        ('google', '谷歌'),
        ('github', 'Github'),
        ('facebook', 'FaceBook'),
        ('qq', 'QQ'),
    )
    type = models.CharField(max_length=10, verbose_name='类型', choices=TYPE, default='a')
    appkey = models.CharField(max_length=200, verbose_name='AppKey')
    appsecret = models.CharField(max_length=200, verbose_name='AppSecret')
    callback_url = models.CharField(max_length=200, verbose_name='回调地址', blank=True, default='http://www.baidu.com')
    is_enable = models.BooleanField(verbose_name='是否显示', default=True, blank=False, null=False)
    created_time = models.DateTimeField(verbose_name='创建时间', default=now)
    last_modify_time = models.DateTimeField(verbose_name='修改时间', default=now)

    def clean(self):
        if AuthConfig.objects.filter(type=self.type).exclude(id=self.id).count():
            raise ValidationError(gettext_lazy(self.type + "已经存在"))

    def __str__(self):
        return self.type

    class Meta:
        db_table = 'db_auth_config'
        verbose_name = 'auth配置'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']

