from django.conf.urls import url
from . import views
urlpatterns=[
    url(r'^place$',views.place),
    url(r'^handle$',views.handle),
    url('^pay$', views.pay),
    url('^query$', views.query),
]