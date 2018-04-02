"""
Django settings for dailyfresh project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import sys

sys.path.insert(1, os.path.join(BASE_DIR, 'apps'))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'e&o%-g1o@-9pgx*_$@8#(2yc2i33dob-5gi_s^am0-eu+&sil6'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tt_users',
    'tt_goods',
    'tt_orders',
    'tt_cart',
    'tinymce',
    'haystack',

)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'dailyfresh.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dailyfresh.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dailyfresh',
        'HOST':'localhost',
        'PORT':'3306',
        'PASSWORD':'mysql',
        'USER':'root',
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'  # 'en-us'

TIME_ZONE = 'Asia/Shanghai'  # 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
AUTH_USER_MODEL='tt_users.User'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
#发送邮件的邮箱
EMAIL_HOST_USER = 'zzgdream888@163.com'
#在邮箱中设置的客户端授权密码
# EMAIL_HOST_PASSWORD = 'knxaqlaypkfjbcjf'
EMAIL_HOST_PASSWORD = 'python88'
# 收件人看到的发件人
EMAIL_FROM = '天天生鲜<zzgdream888@163.com>'

#缓存
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/6",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Session
# http://django-redis-chs.readthedocs.io/zh_CN/latest/#session-backend

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

LOGIN_URL = '/users/login'

DEFAULT_FILE_STORAGE = 'utils.fastdfs.storage.FdfsStorage'

CLIENT_CONF = os.path.join(BASE_DIR, 'utils/fastdfs/client.conf')
SERVER_IP = 'http://192.168.135.3:8888/'

TINYMCE_DEFAULT_CONFIG = {
  'theme': 'advanced', # 丰富样式
  'width': 600,
  'height': 400,
}

#生成静态页面的路径
GENERATE_HTML=os.path.join(BASE_DIR,'static/html')


HAYSTACK_CONNECTIONS = {
  'default': {
      # 使用whoosh引擎：提示，如果不需要使用jieba框架实现分词，就使用whoosh_backend
      # 'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
      'ENGINE': 'haystack.backends.whoosh_cn_backend.WhooshEngine',
      # 索引文件路径
      'PATH': os.path.join(BASE_DIR, 'whoosh_index'),
  }
}
# 当添加、修改、删除数据时，自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

HAYSTACK_SEARCH_RESULTS_PER_PAGE = 2