"""myblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import notifications.urls
from .views import index, aboutus, search, message, message_handle

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', index, name='index'),
    path('aboutus/', aboutus, name='aboutus'),
    path('search/', search, name='search'),
    path('message/', message, name='message'),
    path('message/<int:comment_id>', message_handle, name='message_handle'),
    path('blog/', include('blog.urls')),
    path('user/', include('user.urls')),
    path('likes/', include('likes.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

