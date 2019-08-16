from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation

from ckeditor_uploader.fields import RichTextUploadingField
from statistic.models import ReadCount, AmountOfReading
from likes.models import LikeCount, FavouriteRecord
from user.models import Profile
# Create your models here.


class BlogCategory(models.Model):
    category_name = models.CharField(max_length=15, verbose_name='文章类型')

    class Meta:
        verbose_name = "文章分类"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.category_name

    def getNum(self):
        return Blog.objects.filter(blog_category=self).count()


class Blog(models.Model):
    title = models.CharField(max_length=50, verbose_name='文章标题')
    blog_category = models.ForeignKey(BlogCategory, on_delete=models.DO_NOTHING, verbose_name='文章类型')
    content = RichTextUploadingField(verbose_name='正文')
    author = models.ForeignKey(Profile, related_name='blog_user', on_delete=models.DO_NOTHING, verbose_name='作者')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True)
    is_init = models.BooleanField(verbose_name='是否原创', default=True)
    init_address = models.URLField(verbose_name='原文地址', null=True, blank=True)
    is_replay = models.BooleanField(verbose_name='是否开启留言', default=True)
    aor = GenericRelation(AmountOfReading, related_query_name='blog')

    class Meta:
        verbose_name = "博客信息"
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.title

    def get_read_count(self):
        content_type = ContentType.objects.get_for_model(Blog)
        read_record = ReadCount.objects.filter(object_id=self.id, content_type=content_type).first()
        return read_record.read_num if read_record else 0

    def get_comment_count(self):
        return Comment.objects.filter(blog=self, parent=None).all().count()

    def get_likes_count(self):
        content_type = ContentType.objects.get_for_model(Blog)
        likes_record = LikeCount.objects.filter(object_id=self.id, content_type=content_type).first()
        return likes_record.liked_num if likes_record else 0

    def get_favourite_count(self):
        content_type = ContentType.objects.get_for_model(Blog)
        fav_record = FavouriteRecord.objects.filter(object_id=self.id, content_type=content_type).count()
        return fav_record


class Comment(models.Model):

    blog = models.ForeignKey(Blog, on_delete=models.DO_NOTHING, verbose_name='评论的博客')
    user = models.ForeignKey(Profile, related_name='comment_user', on_delete=models.DO_NOTHING, verbose_name='评论者')
    comment = models.TextField(verbose_name='评论内容')
    is_top = models.BooleanField(default=False, verbose_name='是否置顶')
    is_show = models.BooleanField(default=False, verbose_name='是否为精选')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    parent = models.ForeignKey('self', related_name='related_parent', on_delete=models.CASCADE, blank=True, null=True, verbose_name='上级评论')

    class Meta:
        verbose_name = "评论信息"
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.blog.title

