from django.conf.urls import url
from . import views
urlpatterns=[
    url('^$', views.index),
    url('^fdfs_test$',views.fdfs_test),
]