

from django.db import models

# Create your models here.
from django.utils import timezone
from mdeditor.fields import MDTextField


class TalkTags(models.Model):
    """说说标签模型类"""
    name = models.CharField('说说标签', max_length=256, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'db_talktags'
        verbose_name = '说说标签'
        verbose_name_plural = verbose_name
        ordering = ['id']


class TalkContent(models.Model):
    """说说内容模型类"""
    STATUS_CHOICES = (
        ('Y', '公开'),
        ('N', '私密'),
    )
    body = MDTextField('说说正文')
    created_time = models.DateTimeField(default=timezone.now(), verbose_name='创建时间')
    tag = models.ManyToManyField(TalkTags, verbose_name='说说标签')
    status = models.TextField(choices=STATUS_CHOICES, default='Y', verbose_name='发表状态')

    class Meta:
        db_table = 'db_talk_content'
        verbose_name = '说说内容'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']