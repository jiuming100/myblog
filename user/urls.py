from django.urls import path
from .views import login, logout, register, homepage, homepage_blog_detail, my_favourite, generate, set_repaly, modify_info, modify_nickname, modify_motto, modify_profile, modify_username, modify_password

urlpatterns = [
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('register/', register, name='register'),
    path('homepage/<int:uid>/', homepage, name='homepage'),
    path('blog/<int:blog_id>/', homepage_blog_detail, name='homepage_blog_detail'),
    path('my_favourite/', my_favourite, name='my_favourite'),
    path('generate/', generate, name='generate'),
    path('set_repaly/', set_repaly, name='set_repaly'),
    path('modify_info/', modify_info, name='modify_info'),
    path('modify_nickname/', modify_nickname, name='modify_nickname'),
    path('modify_motto/', modify_motto, name='modify_motto'),
    path('modify_profile/', modify_profile, name='modify_profile'),
    path('modify_username/', modify_username, name='modify_username'),
    path('modify_password/', modify_password, name='modify_password'),
]
