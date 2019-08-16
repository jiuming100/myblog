import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist

from .models import Blog, BlogCategory, Comment
from .utils import get_page
from statistic.models import ReadCount, AmountOfReading
from user.forms import CommentForm, BlogForm
from user.models import Profile
from likes.models import LikeRecord, FavouriteRecord
# Create your views here.


def get_pub_data(request, obj):
    blog_category = BlogCategory.objects.all()
    blog_dates = Blog.objects.dates('create_time', 'month', 'DESC')
    blog_dates_dic = {}
    for blog_date in blog_dates:
        c = Blog.objects.filter(create_time__year=blog_date.year, create_time__month=blog_date.month).count
        blog_dates_dic[blog_date] = c

    dic = {'blog_category': blog_category, 'blog_dates': blog_dates_dic, }
    if obj:
        blogs, page_range = get_page(request, obj)
        dic['blogs'] = blogs
        dic['page_range'] = page_range
    return dic


def blog(request):
    blogs_list = Blog.objects.all()
    return render(request, 'blog.html', get_pub_data(request, blogs_list))


def blog_detail(request, blog_id):
    blog = Blog.objects.filter(id=blog_id).first()
    re_data = get_pub_data(request, None)
    fore = Blog.objects.filter(id__gt=blog_id).last()
    behind = Blog.objects.filter(id__lt=blog_id).first()
    re_data['blog'] = blog
    re_data['fore'] = fore
    re_data['behind'] = behind
    if request.user.is_authenticated:
        re_data['comment_form'] = CommentForm(initial={'blog_id': blog_id})
        re_data['comments'] = Comment.objects.filter(blog=blog, is_show=True, parent=None).order_by('-is_top', 'create_time').all()
        re_data['self_msgs'] = Comment.objects.filter(blog=blog, is_show=False, user__user=request.user, parent=None).order_by('create_time').all()
        #判读是否点赞过
        if LikeRecord.objects.filter(profile__user=request.user, content_type=7, object_id=blog_id).count()>0:
            re_data['islike'] = True
        else:
            re_data['islike'] = False
        # 判读是否收藏
        if FavouriteRecord.objects.filter(profile__user=request.user, content_type=7, object_id=blog_id).count() > 0:
            re_data['isfav'] = True
        else:
            re_data['isfav'] = False
    response = render(request, 'blog_detail.html', re_data)


    #先看看cookie是否存在
    if not request.COOKIES.get('read_num'):
        content_type = ContentType.objects.get_for_model(Blog)
        read_record, create = ReadCount.objects.get_or_create(object_id=blog_id, content_type=content_type)
        read_record.read_num += 1
        read_record.save()

        dd = datetime.datetime.now()
        reading_record, created = AmountOfReading.objects.get_or_create(object_id=blog_id, content_type=content_type,
                                                                  reading_date__year=dd.year, reading_date__month=dd.month,
                                                                  reading_date__day=dd.day)
        if not created:
            reading_record.read_num += 1
        reading_record.save()

        response.set_cookie('read_num', True, max_age=5)
    return response


def categroy(request, type_id):
    blogs_list = Blog.objects.filter(blog_category=type_id)
    categroy_name = BlogCategory.objects.filter(id=type_id).first()
    re_data = get_pub_data(request, blogs_list)
    re_data['categroy_name'] = categroy_name
    return render(request, 'categroy.html', re_data)


def blog_date(request, year, month):
    blogs_list = Blog.objects.filter(create_time__year=year, create_time__month=month)
    re_data = get_pub_data(request,blogs_list)
    re_data['blog_date'] = str(year)+'年'+str(month)+'月'
    return render(request, 'dates.html', re_data)


#读者留言
def comment(request):
    comment_form = CommentForm(request.POST, user=request.user)
    data = {}
    if comment_form.is_valid():
        comment = Comment()
        comment.blog = comment_form.cleaned_data['blog']
        comment.user = Profile.objects.get(user=request.user)
        comment.comment = comment_form.cleaned_data['comment']
        comment.save()
        # 返回数据
        data['status'] = 'SUCCESS'
        data['username'] = comment.user.user.username
        data['comment_time'] = comment.create_time.strftime('%Y-%m-%d %H:%M:%S')
        data['comment'] = comment.comment
        data['id'] = comment.id

        return JsonResponse(data)
    else:
        # 返回数据
        data['status'] = 'FAIL'
        data['message'] = list(comment_form.errors.values())[0][0]

        return JsonResponse(data)


def replay(request):
    comment_form = CommentForm(request.POST, user=request.user)
    data = {}
    if not request.POST.get('comment'):
        data['status'] = 'FAIL'
        data['message'] = '留言不能为空'
        return JsonResponse(data)

    if comment_form.is_valid():
        comment = Comment()
        comment.blog = comment_form.cleaned_data['blog']
        comment.user = Profile.objects.get(user=request.user)
        comment.parent = Comment.objects.filter(id=request.POST.get('comment_id')).first()
        comment.comment = request.POST.get('comment')
        comment.save()
        from notifications.signals import notify
        notify.send(comment.user, recipient=comment.blog.author.user,
                    verb='{}给你的{}留言了'.format(comment.user, comment.blog.title), action_object=comment)
        # 返回数据
        data['status'] = 'SUCCESS'
        data['username'] = comment.user.user.username
        data['comment_time'] = comment.create_time.strftime('%Y-%m-%d %H:%M:%S')
        data['comment'] = comment.comment
        data['id'] = comment.id

        return JsonResponse(data)
    else:
        # 返回数据
        data['status'] = 'FAIL'
        data['message'] = list(comment_form.errors.values())[0][0]

        return JsonResponse(data)


#作者回复留言
def auth_replay(request):
    data = {}
    data['status'] = 'FAIL'

    blog_id = int(request.GET.get('blog_id'))
    comment_id = int(request.GET.get('comment_id'))
    msg = request.GET.get('comment')
    if len(str(msg).strip()) == 0:
        data['status'] = 'FAIL'
        data['message'] = '留言不能为空'
        return JsonResponse(data)

    if Comment.objects.filter(parent_id=comment_id).count()==0:
        comment = Comment()
        replay_comment = Comment.objects.filter(id=comment_id).first()
        comment.blog_id = blog_id
        comment.user = Profile.objects.get(user=request.user)
        comment.parent = replay_comment
        comment.comment = msg
        comment.save()
        data['status'] = 'SUCCESS'
    else:
        data['message'] = '已经留言了'
    return JsonResponse(data)


def is_show(request):
    data = {}
    data['status'] = 'FAIL'

    comment_id = int(request.GET.get('comment_id'))
    is_show = request.GET.get('is_show')
    try:
        comment = Comment.objects.get(id=comment_id)
        show = True if is_show.lower() == 'true' else False
        comment.is_show = show
        if not show and comment.is_top:
            comment.is_top = False
            data['is_top'] = 'false'
        comment.save()
    except ObjectDoesNotExist:
        # 返回数据
        data['message'] = 'fail'
        return JsonResponse(data)

    # 返回数据
    data['status'] = 'SUCCESS'
    data['message'] = '精选成功'
    return JsonResponse(data)


def is_top(request):
    data = {}
    data['status'] = 'FAIL'

    comment_id = int(request.GET.get('comment_id'))
    is_top = request.GET.get('is_top')
    try:
        comment = Comment.objects.get(id=comment_id)
        top = True if is_top.lower() == 'true' else False
        comment.is_top = top
        if top and not comment.is_show:
            comment.is_show = True
            data['is_show'] = 'true'
        comment.save()
    except ObjectDoesNotExist:
        # 返回数据
        data['message'] = 'fail'
        data['message'] = '置顶失败'
        return JsonResponse(data)

    # 返回数据
    data['status'] = 'SUCCESS'
    data['message'] = '置顶操作成功'
    return JsonResponse(data)
