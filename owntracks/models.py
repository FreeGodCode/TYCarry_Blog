from django.db import models

from django.utils.timezone import now


# Create your models here.
class OwnTrackLog(models.Model):
    """docstring"""
    tid = models.CharField(max_length=100, null=False, verbose_name='用户')
    lat = models.FloatField(verbose_name='纬度')
    lon = models.FloatField(verbose_name='经度')
    created_time = models.DateTimeField(verbose_name='创建时间', default=now)

    def __str__(self):
        return self.tid

    class Meta:
        db_table = "db_owntrack_log"
        verbose_name = 'OwnTrackLogs'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']
