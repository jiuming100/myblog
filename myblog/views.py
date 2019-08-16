import datetime

from django.utils import timezone
from django.db.models import Sum, Q
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from notifications.models import Notification
from statistic.models import AmountOfReading
from blog.models import Blog
from blog.utils import get_oneday_hot_blogs, get_somedays_later_hot_blogs
from blog.views import get_pub_data


def index(request):

    reading_data = []
    reading_date = []
    today = timezone.now().date()
    for i in range(6, -1, -1):
        date =today - datetime.timedelta(days=i)
        reading_date.append(date.strftime('%Y-%m-%d'))
        content_type = ContentType.objects.get_for_model(Blog)
        obj_res = AmountOfReading.objects.filter(reading_date=date, content_type=content_type).aggregate(sum_num=Sum('read_num'))
        reading_data.append(obj_res['sum_num'] or 0)
    todays = get_oneday_hot_blogs(today, 'today')
    yesterday = get_oneday_hot_blogs(today - datetime.timedelta(days=1), 'yesterday')
    seven_days = get_somedays_later_hot_blogs(today-datetime.timedelta(days=6), 'sevenday')
    return render(request, 'index.html', {'reading_data': reading_data, 'reading_date': reading_date, 'today': todays, 'yesterday': yesterday, 'seven_days': seven_days})


def aboutus(request):
    return render(request, 'aboutus.html', {})


def search(request):
    content = str(request.GET.get('keyword')).strip()
    blogs = Blog.objects.filter(Q(title__contains=content)|Q(content__contains=content)).all()
    url = 'keyword='+content
    dic = get_pub_data(request, blogs)
    dic['url']=url
    return render(request, 'search.html', dic)


def message(request):
    messages = request.user.notifications.unread()
    return render(request, 'message.html', {'messages': messages})


def message_handle(request, comment_id):
    my_notification = get_object_or_404(Notification, pk=comment_id)
    my_notification.unread = False
    my_notification.save()
    return redirect(my_notification.data['url'])