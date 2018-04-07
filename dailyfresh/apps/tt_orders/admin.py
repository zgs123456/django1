

# Register your models here.
from django.contrib import admin
from .models import OrderInfo

# Register your models here.
class OrderInfoAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'status']


admin.site.register(OrderInfo, OrderInfoAdmin)

