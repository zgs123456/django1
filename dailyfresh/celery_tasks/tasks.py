from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,SignatureExpired
from django.core.mail import send_mail
from celery import Celery
from tt_goods.models import GoodsCategory,IndexCategoryGoodsBanner,IndexPromotionBanner,IndexGoodsBanner

from django.shortcuts import render

from django.conf import settings
import os,django
os.environ.setdefault('DJANGO_SETTINGS_MODULE',"dailyfresh.settings")

app=Celery('celery_tasks.tasks',broker='redis://127.0.0.1:6379/6')

@app.task
def send_user_active(user_id,email):
    # 加密用户编号
    serializer = Serializer(settings.SECRET_KEY, 60 * 60)
    value = serializer.dumps({'id': user_id}).decode()

    # 让用户激活：向注册的邮箱发邮件，点击邮件中的链接，转到本网站的激活地址
    msg = '<a href="http://127.0.0.1:8000/users/active/%s">点击激活</a>' % value
    send_mail('天天生鲜-账户激活','', settings.EMAIL_FROM, [email], html_message=msg)

@app.task
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
