from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import ObjectDoesNotExist
from blog.models import Blog, BlogCategory
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class LoginForm(forms.Form):
    username = forms.CharField(required=True, label='用户名', label_suffix='', error_messages={'required': '用户名不能为空'}, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '用户名'}))
    password = forms.CharField(required=True, label='密码', label_suffix='', min_length=6, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': '密码'}))

    def clean(self):
        username = self.cleaned_data["username"]
        password = self.cleaned_data["password"]
        user = authenticate(username=username, password=password)
        if User.objects.filter(username=username).count() < 1:
            self.add_error('username', '用户不存在')
        if user is None:
            raise forms.ValidationError("用户名或者密码不正确")
        else:
            self.cleaned_data["user"] = user
        return self.cleaned_data


class RegisterForm(forms.Form):
    username = forms.CharField(required=True, error_messages={'required': '用户名不能为空'}, label='用户名', label_suffix='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': '用户名'}))
    password = forms.CharField(required=True, label='密码', label_suffix='', min_length=6, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': '密码'}))
    confirm_pwd = forms.CharField(required=True, label='确认密码', label_suffix='', min_length=6, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': '确认密码'}))
    email = forms.EmailField(required=False, label='邮箱地址', label_suffix='', widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder': '邮箱地址'}))

    def clean_username(self):
        username = self.cleaned_data["username"]
        if username.__len__() < 0:
            raise forms.ValidationError("用户名不能为空")
        if User.objects.filter(username=username).count() > 0:
            raise forms.ValidationError("用户名已存在")
        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        if password.__len__() < 5:
            raise forms.ValidationError("密码不能少于6位")

        return password

    def clean_confirm_pwd(self):
        confirm_pwd = self.cleaned_data['confirm_pwd']
        password = self.cleaned_data['password']
        if confirm_pwd.__len__() < 5:
            raise forms.ValidationError("确认密码不能少于6位")
        if confirm_pwd != password:
            raise forms.ValidationError("确认密码与密码不一致")

        return confirm_pwd


class CommentForm(forms.Form):
    blog_id = forms.IntegerField(widget=forms.HiddenInput)
    comment_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    comment = forms.CharField(required=True, label='', label_suffix='', error_messages={'required': '内容不能为空'}, widget=forms.Textarea(attrs={'class':'form-control','style':'margin-bottom: 10px;height: 100px;resize: none'}))

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(CommentForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 判断用户是否登录
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('用户尚未登录')

        # 评论对象验证
        blog_id = self.cleaned_data['blog_id']
        try:
            blog = Blog.objects.get(pk=blog_id)
            self.cleaned_data['blog'] = blog
        except ObjectDoesNotExist:
            raise forms.ValidationError('评论对象不存在')
        return self.cleaned_data


class BlogForm(forms.Form):
    title = forms.CharField(required=True, error_messages={'required': '标题不能为空'}, label='标题', label_suffix='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': '请输入标题'}))
    content = forms.CharField(required=True, label='文章内容', label_suffix='', error_messages={'required': '内容不能为空'}, widget=CKEditorUploadingWidget(config_name='comment_ckeditor'))
    category = forms.ChoiceField(label='文章分类', label_suffix='', initial=1, choices=((1, '科技'), (2, '娱乐'), (3, '游戏'), (4, '教育'), (5, '汽车'), (6, '文学'), (7, '其他')), widget=forms.Select(attrs={'class':'form-control'}))
    original = forms.BooleanField(required=False, label='原创设置', label_suffix='', initial=True, widget=forms.CheckboxInput(attrs={'onclick': 'toggle_check(this)'}))
    from_address = forms.URLField(required=False, label='原文地址', label_suffix='', widget=forms.URLInput(attrs={'class':'form-control', 'aria-describedby': 'from_address', 'placeholder': '原文地址'}))
    RADIO_CHOICES = (
        (True, "开启留言"),
        (False, "关闭留言"),
    )
    replay = forms.ChoiceField(label='留言设置', label_suffix='', choices=RADIO_CHOICES, initial=True, widget=forms.RadioSelect())

    def clean_title(self):
        title = self.cleaned_data["title"]
        if title.__len__() <= 0:
            raise forms.ValidationError("标题不能为空")
        return title

    def clean_content(self):
        content = self.cleaned_data["content"]
        if content.__len__() <= 0:
            raise forms.ValidationError("正文不能为空")
        return content

    def clean_category(self):
        category = self.cleaned_data["category"]
        if BlogCategory.objects.filter(id=category).count() == 0:
            raise forms.ValidationError("类型提交错误")
        return category

    def clean_from_address(self):
        original = self.cleaned_data["original"]
        from_address = self.cleaned_data["from_address"]
        if not original:
            if from_address.__len__() <= 0:
                raise forms.ValidationError("原文地址不能为空")
        return from_address