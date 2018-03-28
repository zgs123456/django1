from django.shortcuts import render
from .models import GoodsCategory, IndexGoodsBanner, IndexPromotionBanner, IndexCategoryGoodsBanner


def fdfs_test(request):
    category = GoodsCategory.objects.get(pk=1)
    context = {'category': category}
    print(type(category.image))
    # django.db.models.fields.files.ImageFieldFile
    return render(request, 'fdfs_test.html', context)


# Create your views here.



def index(request):
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

    return render(request, 'index.html', context)
