
from django.db import models
from django.contrib.auth.models import AbstractUser
from utils.models import BaseModel


class User(AbstractUser, BaseModel):
    """用户"""
    class Meta:
        db_table = "df_users"

class AreaInfo(models.Model):
    title=models.CharField(max_length=20)
    aParent=models.ForeignKey('self',null=True,blank=True)
    class Meta:
        db_table='df_area'

class Address(BaseModel):
    """地址"""
    receiver_name = models.CharField(max_length=20, verbose_name="收件人")
    province=models.ForeignKey(AreaInfo,related_name='province')
    city = models.ForeignKey(AreaInfo,related_name='city')
    district = models.ForeignKey(AreaInfo,related_name='district')
    phone_number= models.CharField(max_length=11, verbose_name="联系电话")
    addr = models.CharField(max_length=256, verbose_name="详细地址")
    code = models.CharField(max_length=6, verbose_name="邮政编码")
    isDefault =models.BooleanField(default=False)
    class Meta:
        db_table = "df_address"