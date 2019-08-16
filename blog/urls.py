from django.urls import path
from .views import blog, blog_detail, categroy, blog_date, comment, replay, is_show, auth_replay, is_top


urlpatterns = [
    path('', blog, name='blog'),
    path('<int:blog_id>/', blog_detail, name='blog_detail'),
    path('categroy/<int:type_id>/', categroy, name='categroy'),
    path('date/<int:year>/<int:month>/', blog_date, name='date'),
    path('comment/', comment, name='comment'),
    #path('replay/', replay, name='replay'),
    path('auth_replay/', auth_replay, name='auth_replay'),
    path('is_show/', is_show, name='is_show'),
    path('is_top/', is_top, name='is_top'),
]
