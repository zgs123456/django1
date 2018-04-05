import os

from django.conf import settings
from django.shortcuts import render
from django.core.cache import cache
from django_redis import get_redis_connection
from django.core.paginator import Paginator, Page
from .models import GoodsCategory, IndexGoodsBanner, IndexPromotionBanner, IndexCategoryGoodsBanner, GoodsSKU
from  django.http import Http404
from haystack.generic_views import SearchView
from utils.page_list import get_page_list
import json


def fdfs_test(request):
    category = GoodsCategory.objects.get(pk=1)
    context = {'category': category}
    print(type(category.image))
    # django.db.models.fields.files.ImageFieldFile
    return render(request, 'fdfs_test.html', context)


def index(request):
    context = cache.get('index')
    if context is None:
        print('++++++++')  # 测试
        category_list = GoodsCategory.objects.all()
        banner_list = IndexGoodsBanner.objects.all().order_by('index')
        adv_list = IndexPromotionBanner.objects.all().order_by('index')
        for category in category_list:
            category.title_list = IndexCategoryGoodsBanner.objects.filter(display_type=0, category=category).order_by(
                'index')[0:3]
            category.img_list = IndexCategoryGoodsBanner.objects.filter(display_type=1, category=category).order_by(
                'index')[0:4]

        context = {
            'title': '首页',
            'category_list': category_list,
            'banner_list': banner_list,
            'adv_list': adv_list,
        }
        cache.set('index', context, 3600)
    context['total_count'] = get_cart_total(request)
    response = render(request, 'index.html', context)

    return response


def detail(request, sku_id):
    try:
        sku = GoodsSKU.objects.get(pk=sku_id)
    except:
        raise Http404
    category_list = GoodsCategory.objects.all()
    category = sku.category

    new_list = category.goodssku_set.all().order_by('-id')[0:2]
    goods = sku.goods
    # 根据spu找所有的sku，已经“草莓”，找所有的“草莓sku”，如“盒装草莓”、“论斤草莓”...
    other_list = goods.goodssku_set.all()

    # 最近浏览
    if request.user.is_authenticated():
        redis_client = get_redis_connection()
        # 构造键
        key = 'history%d' % request.user.id
        # 如果当前编号已经存在，则删除
        redis_client.lrem(key, 0, sku_id)  # 删除所有的指定元素
        # 将当前编号加入
        redis_client.lpush(key, sku_id)  # 向列表的左侧添加一个元素
        # 不能超过5个，则删除
        if redis_client.llen(key) > 5:  # 判断列表的元素个数
            redis_client.rpop(key)  # 从列表的右侧删除一个元素
            # 查询此商品的评论信息
    comment_list = sku.ordergoods_set.exclude(comment='')

    context = {
        'title': '商品详情',
        'sku': sku,
        'category_list': category_list,
        'new_list': new_list,
        'other_list': other_list,
        'comment_list': comment_list,

    }
    context['total_count'] = get_cart_total(request)
    return render(request, 'detail.html', context)


def list_sku(request, category_id):
    try:
        category_now = GoodsCategory.objects.get(pk=category_id)
    except:
        raise Http404
    order = int(request.GET.get('order', 1))

    if order == 2:
        order_by = '-price'
    elif order == 3:
        order_by = 'price'
    elif order == 4:
        order_by = '-sales'
    else:
        order_by = '-id'

    sku_list = GoodsSKU.objects.filter(category_id=category_id).order_by(order_by)
    paginator = Paginator(sku_list, 1)
    category_list = GoodsCategory.objects.all()
    new_list = category_now.goodssku_set.all().order_by('-id')[0:2]
    total_page = paginator.num_pages
    pindex = int(request.GET.get('pindex', 1))
    if pindex < 1:
        pindex = 1
    if pindex > total_page:
        pindex = total_page
    page = paginator.page(pindex)

    # page_list = []
    # if total_page <= 5:
    #     page_list = range(1, total_page + 1)
    # elif pindex <= 2:
    #     page_list = range(1, 6)
    # elif pindex > total_page - 1:
    #     page_list = range(total_page - 4, total_page + 1)
    # else:
    #     page_list = range(pindex - 2, pindex + 3)
    page_list = get_page_list(total_page, pindex)

    context = {
        'tatle': '商品列表',
        'page': page,
        'category_list': category_list,
        'category_now': category_now,
        'new_list': new_list,
        'order': order,
        'page_list': page_list,
    }
    context['total_count'] = get_cart_total(request)

    return render(request, 'list.html', context)


class MySearchView(SearchView):
    def get(self, request, *args, **kwargs):
        self.curr_request = request
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = '搜索结果'
        context['category_list'] = GoodsCategory.objects.all()

        # 页码控制
        total_page = context['paginator'].num_pages
        pindex = context['page_obj'].number
        context['page_list'] = get_page_list(total_page, pindex)
        context['total_count'] = get_cart_total(self.curr_request)
        return context


def get_cart_total(request):
    total_count = 0
    if request.user.is_authenticated():
        redis_client = get_redis_connection()
        for v in redis_client.hvals('cart%d' % request.user.id):
            total_count += int(v)
    else:
        cart_str = request.COOKIES.get('cart')
        if cart_str:
            cart_dict = json.loads(cart_str)
            for k, v in cart_dict.items():
                total_count += v

    return total_count
