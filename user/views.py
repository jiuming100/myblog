from django.shortcuts import render, redirect, reverse
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db.models import ObjectDoesNotExist
from django.http import JsonResponse

from .models import Profile
from .forms import LoginForm, RegisterForm, CommentForm, BlogForm
from functools import wraps
from blog.models import Blog, Comment, BlogCategory
from blog.views import get_pub_data
from likes.models import FavouriteRecord, LikeRecord


def check_login(f):
    @wraps(f)
    def inner(request, *arg, **kwargs):
        if request.session.get('is_login') == '1':
            return f(request, *arg, **kwargs)
        else:
            return redirect('/user/login')
    return inner


def login(request):

    if request.method == 'GET':
        next = request.META.get('HTTP_REFERER', reverse('index'))
        login_form = LoginForm()

    else:
        login_form = LoginForm(request.POST)
        next = request.POST.get('next')
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            return redirect(next)
    return render(request, 'login.html', {'login_form': login_form, 'next': next})


def logout(request):
    auth.logout(request)
    return redirect(reverse('index'))


def register(request):
    if request.method == 'POST':
        register_form = RegisterForm(request.POST)
        next = request.POST.get('next')
        if register_form.is_valid():
            user = User()
            user.username = register_form.cleaned_data['username']
            user.password = make_password(register_form.cleaned_data['password'])
            email = request.POST.get('email')
            if email:
                user.email = email
            user.save()
            profile = Profile(user=user)
            profile.save()
            auth.login(request, user)
            return render(request, 'tips.html', {'info': '注册成功', 'jumpto': next})
        else:
            return render(request, 'register.html', {'register_form': register_form, 'next': next})

    else:
        register_form = RegisterForm()
        next = request.META.get('HTTP_REFERER', reverse('index'))
        return render(request, 'register.html', {'register_form': register_form, 'next': next})


def get_recent_blogs(request):
    blogs_recent = Blog.objects.filter(author__user=request.user).all().order_by('-create_time')[:5]
    return blogs_recent


def homepage(request, uid):
    profile = Profile.objects.filter(id=uid).first()
    blogs_list = Blog.objects.filter(author=profile).all()
    dic = get_pub_data(request, blogs_list)
    dic['blogs_recent'] = get_recent_blogs(request)
    dic['author'] = profile
    return render(request, 'homepage.html', dic)


def homepage_blog_detail(request, blog_id):
    blog = Blog.objects.filter(id=blog_id).first()
    re_data = get_pub_data(request, None)
    fore = Blog.objects.filter(id__gt=blog_id, author=blog.author).last()
    behind = Blog.objects.filter(id__lt=blog_id, author=blog.author).first()
    re_data['blog'] = blog
    re_data['fore'] = fore
    re_data['behind'] = behind
    blogs_recent = Blog.objects.filter(author_id=blog.author_id).order_by('-create_time')[:5]
    re_data['blogs_recent'] = blogs_recent
    re_data['author'] = blog.author

    if blog.author.user == request.user:

        comments = Comment.objects.filter(blog_id=blog_id, parent=None).order_by('create_time').all()
        re_data['comments'] = comments
        return render(request, 'homepage_blog_detail.html', re_data)
    else:
        if request.user.is_authenticated:
            re_data['comment_form'] = CommentForm(initial={'blog_id': blog_id})
            re_data['comments'] = Comment.objects.filter(blog=blog, is_show=True, parent=None).order_by('-is_top',
                                                                                                        'create_time').all()
            re_data['self_msgs'] = Comment.objects.filter(blog=blog, is_show=False, user_id=request.user.id,
                                                          parent=None).order_by('create_time').all()

            # 判读是否点赞过
            if LikeRecord.objects.filter(profile__user=request.user, content_type=7, object_id=blog_id).count() > 0:
                re_data['islike'] = True
            else:
                re_data['islike'] = False
            # 判读是否收藏
            if FavouriteRecord.objects.filter(profile__user=request.user, content_type=7,
                                              object_id=blog_id).count() > 0:
                re_data['isfav'] = True
            else:
                re_data['isfav'] = False

        return render(request, 'user_blog_detail.html', re_data)


def my_favourite(request):
    if request.user.is_authenticated:
        fr = FavouriteRecord.objects.filter(profile__user=request.user).order_by('-liked_time').values('object_id')
        blogs=[]
        for i in fr:
            blogs.append(Blog.objects.get(id=i['object_id']))
        dic = get_pub_data(request, blogs)
        dic['blogs_recent'] = get_recent_blogs(request)
        dic['author'] = request.user.user_profile
        return render(request, 'my_favourite.html', dic)
    else:
        return redirect(reverse('login'))


def generate(request):

    if request.method == 'GET':
        blog_form = BlogForm()
        return render(request, 'generate.html', {'blog_form': blog_form})

    blog_form = BlogForm(request.POST)
    if blog_form.is_valid():
        title = blog_form.cleaned_data['title']
        content = blog_form.cleaned_data['content']
        category = blog_form.cleaned_data['category']
        original = blog_form.cleaned_data['original']
        from_address = blog_form.cleaned_data['from_address']
        is_replay = blog_form.cleaned_data['replay']
        print(title, content, category, original, from_address, is_replay)
        blog = Blog()
        blog.title = title
        blog.content = content
        blog.blog_category = BlogCategory.objects.get(id=category)
        blog.author = request.user.user_profile
        blog.is_init = original
        blog.is_replay = is_replay
        blog.init_address = from_address
        blog.save()
        return render(request, 'tips.html', {'info': '保存成功','jumpto':reverse('homepage_blog_detail', kwargs={'blog_id': blog.id})})
    return render(request, 'generate.html', {'blog_form': blog_form})


def set_repaly(request):
    data = {}
    data['status'] = 'FAIL'
    blog_id = int(request.GET.get('blog_id'))
    is_replay = True if request.GET.get('is_replay') == 'True' else False

    try:
        blog = Blog.objects.get(id=blog_id)
        if is_replay != blog.is_replay:
            data['message'] = '状态不需要更改'
            return JsonResponse(data)
        else:
            blog.is_replay = not is_replay
            blog.save()
            if blog.comment_set.count() > 0:
                data['commentv'] = 'YES'
            else:
                data['comment'] = 'NO'
            data['status'] = 'SUCCESS'
            return JsonResponse(data)
    except ObjectDoesNotExist:
        data['message'] = '博客不存在'
        return JsonResponse(data)


def modify_info(request):
    user = request.user
    profile = user.user_profile
    return render(request, 'modify_info.html', {'profile': profile})


def modify_nickname(request):
    data = {}
    data['status'] = 'FAIL'
    nickname = request.POST.get('nickname')
    try:
        profile = Profile.objects.get(user=request.user)
        profile.nickname = nickname
        profile.save()
        data['status'] = 'SUCCESS'
        data['message'] = '昵称修改成功'
    except ObjectDoesNotExist:
        data['message'] = '用户不存在'
    return JsonResponse(data)


def modify_motto(request):
    data = {}
    data['status'] = 'FAIL'
    motto = request.POST.get('motto')
    try:
        profile = Profile.objects.get(user=request.user)
        profile.motto = motto
        profile.save()
        data['status'] = 'SUCCESS'
        data['message'] = '座右铭修改成功'
    except ObjectDoesNotExist:
        data['message'] = '用户不存在'
    return JsonResponse(data)


def modify_profile(request):
    data = {}
    data['status'] = 'FAIL'
    pro = request.POST.get('profile')
    try:
        profile = Profile.objects.get(user=request.user)
        profile.profile = pro
        profile.save()
        data['status'] = 'SUCCESS'
        data['message'] = '个人简介修改成功'
    except ObjectDoesNotExist:
        data['message'] = '用户不存在'
    return JsonResponse(data)


def modify_username(request):
    data = {}
    data['status'] = 'FAIL'
    username = request.POST.get('username')
    if User.objects.filter(username=username).count()>0:
        data['message'] = '用户名存在'
        return JsonResponse(data)
    try:
        profile = Profile.objects.get(user=request.user)
        profile.user.username = username
        profile.user.save()
        data['status'] = 'SUCCESS'
        data['message'] = '用户名修改成功'
    except ObjectDoesNotExist:
        data['message'] = '用户不存在'
    return JsonResponse(data)


def modify_password(request):
    data = {}
    data['status'] = 'FAIL'
    password = request.POST.get('password')
    password1 = request.POST.get('password1')
    if len(password) <6:
        data['message'] = '密码不能少于6位！'
        return JsonResponse(data)
    if password != password1:
        data['message'] = '密码不一致'
        return JsonResponse(data)
    try:
        profile = Profile.objects.get(user=request.user)
        profile.user.password = make_password(password)
        profile.user.save()
        data['status'] = 'SUCCESS'
        data['message'] = '密码修改成功'
        auth.logout(request)
    except ObjectDoesNotExist:
        data['message'] = '用户不存在'
    return JsonResponse(data)