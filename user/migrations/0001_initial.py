# Generated by Django 2.1.7 on 2019-08-01 07:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nickname', models.CharField(default=None, max_length=20, null=True, verbose_name='昵称')),
                ('profile', models.TextField(default='', verbose_name='个人简介')),
                ('motto', models.CharField(default='', max_length=100, verbose_name='座右铭')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '个人信息',
                'verbose_name_plural': '个人信息',
            },
        ),
    ]
