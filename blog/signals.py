from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from notifications.signals import notify

from .models import Comment


@receiver(post_save, sender=Comment)
def my_message(sender, instance, **kwargs):
    if instance.parent:
        #作者留言
        verb = '作者回复了你的留言:“{}”,说：“{}”'.format(instance.parent.comment, instance.comment)
        url = reverse('blog_detail', args=(instance.blog.id,))+'#comment_' + str(instance.parent.id)
        print('url:' + url)
        notify.send(instance.blog.author, recipient=instance.user.user, verb=verb, action_object=instance, url=url)
    else:
        verb=''
        url = reverse('blog_detail', args=(instance.blog.id,))+'#comment_' + str(instance.id)
        print('url:'+url)
        if instance.is_show:
            if instance.is_top:
                verb = '您的留言:“{}”被置顶了'.format(instance.comment)
            else:
                verb = '您的留言:“{}”已被作者审核通过'.format(instance.comment)
        else:
            verb = '{}给你的文章《{}》留言了！说：“{}”'.format(instance.user, instance.blog.title, instance.comment)
            url = reverse('homepage_blog_detail', args=(instance.blog.id,))+'#comment_' + str(instance.id)
        notify.send(instance.user, recipient=instance.blog.author.user, verb=verb, action_object=instance, url=url)

