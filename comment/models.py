from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


# Create your models here.
class Comment(models.Model):
    """评论模型类"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name='评论来源')
    object_id = models.PositiveIntegerField(verbose_name='评论对象')
    content_object = GenericForeignKey('content_type', 'object_id')

    text = RichTextField('评论内容')
    comment_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='评论用户')

    root = models.ForeignKey('self', related_name='root_comment', null=True, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', related_name='parent_comment', null=True, on_delete=models.CASCADE)
    reply_to = models.ForeignKey(User, related_name='replies', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.text

    class Meta:
        db_table = 'db_comment'
        verbose_name = '我的评论'
        verbose_name_plural = verbose_name
        ordering = ['-comment_time']

