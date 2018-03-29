import os


from django.conf import settings
from django.shortcuts import render
from django.core.cache import cache
from django_redis import get_redis_connection
from django.core.paginator import Paginator,Page
from .models import GoodsCategory, IndexGoodsBanner, IndexPromotionBanner, IndexCategoryGoodsBanner, GoodsSKU
from  django.http import Http404

def fdfs_test(request):
    category = GoodsCategory.objects.get(pk=1)
    context = {'category': category}
    print(type(category.image))
    # django.db.models.fields.files.ImageFieldFile
    return render(request, 'fdfs_test.html', context)


# Create your views here.



def index(request):

    context=cache.get('index')
    if context is None:
        print('++++++++') #测试
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

    response=render(request,'index.html',context)


    return response


def detail(request,sku_id):
    try:
        sku=GoodsSKU.objects.get(pk=sku_id)
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

    context={
        'title':'商品详情',
        'sku':sku,
        'category_list':category_list,
        'new_list': new_list,
        'other_list': other_list,


    }
    return  render(request,'detail.html',context)


def list_sku(request,category_id):
    try:
        category_now=GoodsCategory.objects.get(pk=category_id)
    except:
        raise  Http404
    sku_list=GoodsSKU.objects.filter(category_id=category_id).order_by('-id')
    paginator=Paginator(sku_list,15)
    page=paginator.page(1)
    category_list=GoodsCategory.objects.all()
    category_now=GoodsCategory.objects.get(pk=category_id)
    new_list=category_now.goodssku_set.all().order_by('-id')[0:2]
    context={
        'tatle':'商品列表',
        'page':page,
        'category_list':category_list,
        'category_now':category_now,
        'new_list':new_list,
    }
    return render(request,'list.html',context)
