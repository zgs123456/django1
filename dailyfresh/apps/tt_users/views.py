from django.contrib.auth import authenticate,login
from django.shortcuts import render,redirect
from django.views.generic.base import View
from django.http import HttpResponse,JsonResponse
from .models import User
import re
from django.core.mail import send_mail
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired


# Create your views here.

class RegisterView(View):
    '''类视图 ：处理数据'''

    def get(self, request):
        """处理GET请求，返回注册页面"""
        return render(request,'register.html')

    def post(self, request):

        """ 获取注册请求参数"""
        dict=request.POST
        uname = dict.get('user_name')
        pwd = dict.get('pwd')
        cpwd = dict.get('cpwd')
        email = dict.get('email')
        allow = dict.get('allow')
        context={
            'uname': uname,
            'pwd': pwd,
            'email': email,
            'cpwd': cpwd,
            'err_msg': '',
            'title': '注册处理',
        }


        # 判断是否勾选协
        if allow is None:
            context['err_msg'] = '请接收协议'
            return render(request, 'register.html', context)

        # 参数校验：缺少任意一个参数，就不要在继续执行
        if not all([uname, pwd,cpwd,email]):
            context['err_msg'] = '请填写完整信息'
            return render(request,'register.html',context)

        if pwd != cpwd:
            context['err_msg'] = '两次密码不一致'
            return render(request, 'register.html', context)

        # 判断邮箱
        if not re.match(r"^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$", email):
            context['err_msg'] = '邮箱格式不正确'
            return render(request, 'register.html', context)
        #看用户是否存在
        if User.objects.filter(username=uname).count()>0:
            context['err_msg'] = '用户名已经存在'
            return render(request, 'register.html', context)
        #邮箱是否被使用
        # if User.objects.filter(email=email).count() > 0:
        #     context['errmsg'] = '邮箱已经被注册'
        #     return render(request, 'register.html', context)

        # 保存数据到数据库

        user = User.objects.create_user(uname, email, pwd)

        # 手动的将用户认证系统默认的激活状态is_active设置成False,默认是True
        user.is_active = False
        # 保存数据到数据库
        user.save()

        #加密用户编号
        serializer=Serializer(settings.SECRET_KEY,60*60*24*100)
        value=serializer.dumps({'id': user.id}).decode()

        #让用户激活：向注册的邮箱发邮件，点击邮件中的链接，转到本网站的激活地址
        msg='<a href="http://127.0.0.1:8000/users/active/%s">点击激活</a>' % value
        send_mail('天天生鲜-账户激活','',settings.EMAIL_FROM,[email],html_message=msg)


        return HttpResponse('这里实现注册逻辑')

def active(request,value):
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
        uname=request.COOKIES.get('uname','')
        context={
            'title': '登录',
            'uname':uname
        }
        return render(request, 'login.html',context)

    def post(self, request):
        # 接收数据
        dict = request.POST
        uname = dict.get('username')
        upwd = dict.get('pwd')
        remember=dict.get('remember')

        # 构造返回结果
        context = {
            'uname': uname,
            'upwd': upwd,
            'err_msg': '',
            'title':'登录处理',
        }

        # 判断数据是否填写
        if not all([uname, upwd]):
            context['err_msg'] = '请填写完整信息'
            return render(request,'login.html', context)

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

        response=redirect('/users/info')

        #记住用户名
        if remember is None:
            response.delete_cookie('uname')
        else:
            response.set_cookie('uname',uname,expires=60*60*24*7)

        # 如果登录成功则转到用户中心页面
        return response


