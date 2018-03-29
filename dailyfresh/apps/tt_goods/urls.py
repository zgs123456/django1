from django.conf.urls import url
from . import views
urlpatterns=[
    url('^index$', views.index),
    url('^fdfs_test$',views.fdfs_test),
    url(r'^(\d+)$',views.detail),
    url(r'^list(\d+)$', views.list_sku),
]