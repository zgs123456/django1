import os

from django.shortcuts import render
from django.conf import settings

from .models import GoodsCategory,Goods,GoodsSKU,GoodsImage,IndexGoodsBanner,IndexCategoryGoodsBanner,IndexPromotionBanner
from django.contrib import admin
from django.core.cache import cache
# from celery_tasks.tasks import generate_html
# Register your models here.
class BaseAdmin(admin.ModelAdmin):


    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        generate_html()
        cache.delete('index')
    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        generate_html()
        cache.delete('index')
def generate_html():
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
    response = render(None, 'index.html', context)

    html= response.content.decode()
    with open(os.path.join(settings.GENERATE_HTML,'index.html'),'w') as f1:
        f1.write(html)


class GoodsCategoryAdmin(BaseAdmin):
    list_display = ['id', 'name', 'logo']


class IndexCategoryGoodsBannerAdmin(BaseAdmin):
    pass


class IndexPromotionBannerAdmin(BaseAdmin):
    pass


class IndexGoodsBannerAdmin(BaseAdmin):
    pass


admin.site.register(GoodsCategory, GoodsCategoryAdmin)
admin.site.register(Goods)
admin.site.register(GoodsSKU)
admin.site.register(GoodsImage)
admin.site.register(IndexCategoryGoodsBanner, IndexCategoryGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)


