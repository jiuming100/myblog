from django.contrib import admin
from .models import ReadCount, AmountOfReading
# Register your models here.


@admin.register(ReadCount)
class ReadCountAdmin(admin.ModelAdmin):
    list_display = ['id', 'read_num', 'content_type']


@admin.register(AmountOfReading)
class AmountOfReadingAdmin(admin.ModelAdmin):
    list_display = ['id', 'read_num', 'reading_date', 'content_type']