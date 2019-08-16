from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
# Create your models here.


class ReadCount(models.Model):
    read_num = models.IntegerField(default=0)

    content_type = models.ForeignKey(to=ContentType, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = "阅读统计"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.read_num


class AmountOfReading(models.Model):
    read_num = models.IntegerField(default=1)
    reading_date = models.DateField(auto_now_add=True)

    content_type = models.ForeignKey(to=ContentType, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = "每篇阅读量统计"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.read_num