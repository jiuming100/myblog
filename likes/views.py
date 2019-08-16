from django.shortcuts import render, reverse
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.db.models import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from .models import LikeCount, LikeRecord, FavouriteRecord
from user.models import Profile


def ErrorResponse(code, message):
    data = {}
    data['status'] = 'ERROR'
    data['code'] = code
    data['message'] = message
    return JsonResponse(data)

def SuccessResponse(liked_num):
    data = {}
    data['status'] = 'SUCCESS'
    data['liked_num'] = liked_num
    return JsonResponse(data)

def SuccessFavResponse():
    data = {}
    data['status'] = 'SUCCESS'
    return JsonResponse(data)


def like(request):
    # 获取数据
    try:
        user = Profile.objects.get(user=request.user)
        if not user.user.is_authenticated:
            return ErrorResponse(400, 'you were not login')
    except Exception:
        return ErrorResponse(400, 'user not exist')

    content_type = request.GET.get('content_type')
    object_id = int(request.GET.get('object_id'))
    try:
        content_type = ContentType.objects.get(model=content_type)
        model_class = content_type.model_class()
        model_obj = model_class.objects.get(pk=object_id)
    except ObjectDoesNotExist:
        return ErrorResponse(401, 'object not exist')

    if request.GET.get('is_like') == 'true':
        like_record, created = LikeRecord.objects.get_or_create(content_type=content_type, object_id=object_id,
                                                                profile=user)
        if created:
            # 未点赞过，进行点赞
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            like_count.liked_num += 1
            like_count.save()
            return SuccessResponse(like_count.liked_num)
        else:
            # 已点赞过，不能重复点赞
            return ErrorResponse(402, '已点赞过，不能重复点赞')

    else:
        # 要取消点赞
        if LikeRecord.objects.filter(content_type=content_type, object_id=object_id, profile=user).exists():
            # 有点赞过，取消点赞
            like_record = LikeRecord.objects.get(content_type=content_type, object_id=object_id, profile=user)
            like_record.delete()
            # 点赞总数减1
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            if not created:
                like_count.liked_num -= 1
                like_count.save()
                return SuccessResponse(like_count.liked_num)
            else:
                return ErrorResponse(404, 'data error')
        else:
            # 没有点赞过，不能取消
            return ErrorResponse(403, 'you were not liked')


def favourite(request):
    # 获取数据
    try:
        user = Profile.objects.get(user=request.user)
        if not user.user.is_authenticated:
            return ErrorResponse(400, 'you were not login')
    except Exception:
            return ErrorResponse(400, 'User does not exist!')

    content_type = request.GET.get('content_type')
    object_id = int(request.GET.get('object_id'))
    try:
        content_type = ContentType.objects.get(model=content_type)
        model_class = content_type.model_class()
        model_obj = model_class.objects.get(pk=object_id)
    except ObjectDoesNotExist:
        return ErrorResponse(401, 'object not exist')

    if request.GET.get('is_fav') == 'true':
        fav_record, created = FavouriteRecord.objects.get_or_create(content_type=content_type, object_id=object_id,
                                                                profile=user)
        if created:
            # 未点收藏，进行收藏
            return SuccessFavResponse()
        else:
            # 已点赞过，不能重复点赞
            return ErrorResponse(402, '已点赞过，不能重复点赞')

    else:
        # 要取消收藏
        if FavouriteRecord.objects.filter(content_type=content_type, object_id=object_id, profile=user).exists():
            # 已收藏，取消收藏
            like_record = FavouriteRecord.objects.get(content_type=content_type, object_id=object_id, profile=user)
            like_record.delete()

            return SuccessFavResponse()
        else:
            # 未收藏，不能取消收藏
            return ErrorResponse(403, 'you were not liked')