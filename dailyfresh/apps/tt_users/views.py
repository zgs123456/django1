from django.shortcuts import render, redirect
from django.views.generic import View
from .models import User, Address, AreaInfo
import re
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
from celery_tasks.tasks import send_user_active
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from utils.views import LoginRequiredViewMixin
from django_redis import get_redis_connection
from tt_goods.models import GoodsSKU
import json
from tt_orders.models import OrderInfo
from django.core.paginator import Paginator, Page
from utils.page_list import get_page_list


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html', {'title': '注册'})

    def post(self, request):
        # 接收数据
        dict = request.POST
        uname = dict.get('user_name')
        pwd = dict.get('pwd')
        cpwd = dict.get('cpwd')
        email = dict.get('email')
        uallow = dict.get('allow')

        # 结果数据
        context = {
            'uname': uname,
            'pwd': pwd,
            'email': email,
            'cpwd': cpwd,
            'err_msg': '',
            'title': '注册处理',
        }

        # 判断数据的有效性

        # 1.判断是否接收协议
        if uallow is None:
            context['err_msg'] = '请接收协议'
            return render(request, 'register.html', context)

        # 2.验证数据不为空
        if not all([uname, pwd, cpwd, email]):
            context['err_msg'] = '请填写完整信息'
            return render(request, 'register.html', context)

        # 3.判断两个密码一致
        if pwd != cpwd:
            context['err_msg'] = '两次密码不一致'
            return render(request, 'register.html', context)

        # 4.用户名不能重复
        if User.objects.filter(username=uname).count() > 0:
            context['err_msg'] = '用户名已经存在'
            return render(request, 'register.html', context)

        # 5.邮箱格式是否正确
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            context['err_msg'] = '邮箱格式不正确'
            return render(request, 'register.html', context)

        # 6.邮箱是否存在
        # if User.objects.filter(email=email).count()>0:
        #     context['err_msg']='邮箱已经被注册'
        #     return render(request,'register.html',context)

        # 保存对象
        user = User.objects.create_user(uname, email, pwd)
        user.is_active = False
        user.save()

        # 加密用户编号
        # serializer=Serializer(settings.SECRET_KEY,60*60)
        # value=serializer.dumps({'id':user.id}).decode()
        # #让用户激活：向注册的邮箱发邮件，点击邮件中的链接，转到本网站的激活地址
        # msg='<a href="http://127.0.0.1:8000/users/active/%s">点击激活</a>'%value
        # send_mail('天天生鲜-账户激活','',settings.EMAIL_FROM,[email],html_message=msg)

        # 通知celery执行此任务，并传递参数user
        send_user_active.delay(user.id, user.email)
        # 提示
        return HttpResponse('注册成功，请稍候到邮箱中激活账户')


def active(request, value):
    # 解密
    try:
        serializer = Serializer(settings.SECRET_KEY)
        dict = serializer.loads(value)
    except SignatureExpired as e:
        return HttpResponse('链接已经过期')

    # 激活指定的账户
    uid = dict.get('id')
    user = User.objects.get(pk=uid)
    user.is_active = True
    user.save()

    return redirect('/users/login')


def exists(request):
    # 接收用户名
    uname = request.GET.get('uname')

    if uname is not None:
        # 判断用户名是否存在
        result = User.objects.filter(username=uname).count()

    # 返回结果
    return JsonResponse({'result': result})


class LoginView(View):
    def get(self, request):
        uname = request.COOKIES.get('uname', '')
        context = {
            'title': '登录',
            'uname': uname
        }
        return render(request, 'login.html', context)

    def post(self, request):
        # 接收数据
        dict = request.POST
        uname = dict.get('username')
        upwd = dict.get('pwd')
        remember = dict.get('remember')

        # 构造返回结果
        context = {
            'uname': uname,
            'upwd': upwd,
            'err_msg': '',
            'title': '登录处理',
        }

        # 判断数据是否填写
        if not all([uname, upwd]):
            context['err_msg'] = '请填写完整信息'
            return render(request, 'login.html', context)

        # 判断用户名、密码是否正确
        user = authenticate(username=uname, password=upwd)

        if user is None:
            context['err_msg'] = '用户名或密码错误'
            return render(request, 'login.html', context)

        # 如果未激活也不允许登录
        if not user.is_active:
            context['err_msg'] = '请先到邮箱中激活'
            return render(request, 'login.html', context)

        # 状态保持
        login(request, user)

        # 获取next参数，转回到之前的页面
        # http://127.0.0.1:8000/user/login?next=/user/order
        # http://127.0.0.1:8000/user/login?next=/user/site
        next_url = request.GET.get('next', '/users/info')
        response = redirect(next_url)

        # 记住用户名
        if remember is None:
            response.delete_cookie('uname')
        else:
            response.set_cookie('uname', uname, expires=60 * 60 * 24 * 7)

        # 如果登录成功则转到用户中心页面
        # 读取cookie
        cart_str = request.COOKIES.get('cart')
        if cart_str:
            key = 'cart%d' % request.user.id
            redis_client = get_redis_connection()
            cart_dict = json.loads(cart_str)
            for k, v in cart_dict.items():
                # 判断购物车里是否有数据
                if redis_client.hexists(key, k):
                    # 有数据追加
                    count1 = int(redis_client.hget(key, k))
                    count2 = v
                    count3 = count1 + count2
                    if count3 > 5:
                        count3 = 5
                    redis_client.hset(key, k, count3)
                else:
                    # 没有数据直接加数据
                    redis_client.hset(key, k, v)

            response.delete_cookie('cart')

        return response


def logout_user(request):
    # 退出用户
    logout(request)

    return redirect('/users/login')


@login_required
def info(request):
    # 如果用户未登录，则转到登录页面
    if not request.user.is_authenticated():
        return redirect('/users/login?next=' + request.path)

    # 查询当前用户的默认收货地址,如果没有数据则返回[]
    address = request.user.address_set.filter(isDefault=True)
    if address:
        address = address[0]
    else:
        address = None

    # 获取redis服务器的连接,根据settings.py中的caches的default获取
    redis_client = get_redis_connection()
    # 因为redis中会存储所有用户的浏览记录，所以在键上需要区分用户
    gid_list = redis_client.lrange('history%d' % request.user.id, 0, -1)
    # 根据商品编号查询商品对象
    goods_list = []
    for gid in gid_list:
        goods_list.append(GoodsSKU.objects.get(pk=gid))

    context = {
        'title': '个人信息',
        'address': address,
        'goods_list': goods_list
    }
    return render(request, 'user_center_info.html', context)


@login_required
def order(request):
    order_list = OrderInfo.objects.filter(user=request.user)
    paginator = Paginator(order_list, 2)
    total_page = paginator.num_pages

    pindex = int(request.GET.get('pindex', 1))
    if pindex <= 1:
        pindex = 1
    if pindex >= total_page:
        pindex = total_page

    page = paginator.page(pindex)
    page_list = get_page_list(total_page, pindex)
    context = {
        'title': '我的订单',
        'page': page,
        'page_list': page_list,
    }
    return render(request, 'user_center_order.html', context)


# django中类视图添加装饰器推荐的方案Mixin
# class SiteView(View):RedirectView
# class SiteView(LoginRequiredView):
class SiteView(LoginRequiredViewMixin, View):  # RedirectView
    def get(self, request):
        # 查询当前用户的收货地址
        addr_list = Address.objects.filter(user=request.user)

        context = {
            'title': '收货地址',
            'addr_list': addr_list,
        }
        return render(request, 'user_center_site.html', context)

    def post(self, request):
        # 接收数据
        dict = request.POST
        receiver = dict.get('receiver')
        provice = dict.get('provice')  # 选中的option的value值
        city = dict.get('city')
        district = dict.get('district')
        addr = dict.get('addr')
        code = dict.get('code')
        phone = dict.get('phone')
        default = dict.get('default')

        # 验证有效性
        if not all([receiver, provice, city, district, addr, code, phone]):
            return render(request, 'user_center_site.html', {'err_msg': '信息填写不完整'})

        # 保存数据
        address = Address()
        address.receiver = receiver
        address.province_id = provice
        address.city_id = city
        address.district_id = district
        address.addr = addr
        address.code = code
        address.phone_number = phone
        if default:
            address.isDefault = True
        address.user = request.user
        address.save()

        # 返回结果
        return redirect('/users/site')


def area(request):
    # 获取上级地区的编号
    pid = request.GET.get('pid')

    if pid is None:
        # 查询省信息[area,]
        slist = AreaInfo.objects.filter(aParent__isnull=True)
    else:
        # 查询指定pid的子级地区
        # 如果pid是省的编号，则查出来市的信息
        # 如果pid是市的编号，则查出来区县的信息
        slist = AreaInfo.objects.filter(aParent_id=pid)

    # 将数据的结构整理为：[{id:**,title:***},{},...]
    slist2 = []
    for s in slist:
        slist2.append({'id': s.id, 'title': s.title})

    return JsonResponse({'list': slist2})
def urltest(request):
    return HttpResponse('ok')


class CommentView(LoginRequiredViewMixin, View):
    def get(self, request):
        order_id = request.GET.get('order_id')

        order = OrderInfo.objects.get(pk=order_id)

        context = {
            'title': '评论商品',
            'order': order,
        }
        return render(request, 'user_center_comment.html', context)

    def post(self, request):
        #虽然当前请求方式为post，但是order_id是在地址中的参数，所以使用GET来接收
        order_id = request.GET.get('order_id')

        order = OrderInfo.objects.get(pk=order_id)
        order.status = 5
        order.save()

        dict = request.POST

        for detail in order.ordergoods_set.all():
            detail.comment = dict.get(str(detail.id))
            detail.save()
        return redirect('/users/order')
