from django.contrib import admin
from .models import BlogCategory, Blog, Comment
# Register your models here.


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'category_name']


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'blog_category', 'content', 'author', 'create_time']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['blog', 'user', 'comment', 'parent', 'is_top', 'is_show', 'create_time']