from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.core.cache import cache
from .models import Blog
from statistic.models import AmountOfReading


def get_page(request, obj):
    paginator = Paginator(obj, settings.PAGINATION_SETTINGS['PER_PAGE'])
    page = request.GET.get(settings.PAGINATION_SETTINGS['KEY_WORD'])
    obj_list = paginator.get_page(page)
    current_page = obj_list.number
    page_range = list(range(max(current_page-2, 1), current_page))+list(range(current_page, min(current_page+2, paginator.num_pages)+1))
    if page_range[0] >= 2:
        if page_range[0]-2 > 0:
            page_range.insert(0, '...')
        page_range.insert(0, 1)
    if page_range[-1] < paginator.num_pages:
        if paginator.num_pages - page_range[-1] > 1:
            page_range.append('...')
        page_range.append(paginator.num_pages)
    return obj_list, page_range


def get_oneday_hot_blogs(date, cache_name):
    if cache.get(cache_name) is None:
        content_type = ContentType.objects.get_for_model(Blog)
        obj_res = Blog.objects.filter(aor__reading_date=date, aor__content_type=content_type).values('id','title', 'aor__read_num') \
                                                                .order_by('-aor__read_num')[:5]
        cache.set(cache_name, obj_res, 60)
    else:
        obj_res = cache.get(cache_name)
    return obj_res


def get_somedays_later_hot_blogs(date, cache_name):
    if cache.get(cache_name) is None:
        content_type = ContentType.objects.get_for_model(Blog)
        obj_res = Blog.objects.filter(aor__reading_date__gte=date, aor__content_type=content_type) \
                      .values('aor__object_id', 'title') \
                      .annotate(read_sum=Sum('aor__read_num')).order_by('-read_sum')[:5]
        cache.set(cache_name, obj_res, 1)
    else:
        obj_res = cache.get(cache_name)
    return obj_res

