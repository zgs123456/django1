from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,SignatureExpired
from django.conf import settings
from django.core.mail import send_mail
from celery import Celery

from django.conf import settings
import os,django
os.environ.setdefault('DJANGO_SETTINGS_MODULE',"dailyfresh.settings")

app=Celery('celery_tasks.tasks',broker='redis://127.0.0.1:6379/6')
django.setup()
@app.task
def send_user_active(user_id,email):
    # 加密用户编号
    serializer = Serializer(settings.SECRET_KEY, 60 * 60)
    value = serializer.dumps({'id': user_id}).decode()

    # 让用户激活：向注册的邮箱发邮件，点击邮件中的链接，转到本网站的激活地址
    msg = '<a href="http://127.0.0.1:8000/users/active/%s">点击激活</a>' % value
    send_mail('天天生鲜-账户激活','', settings.EMAIL_FROM, [email], html_message=msg)

@app.task
def say_ok():
    pass
