from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django_redis import get_redis_connection
from tt_goods.models import GoodsSKU
from django.db import transaction
from django.http import Http404, JsonResponse
from .models import OrderInfo, OrderGoods
import uuid
from django.db import transaction
from django.db.models import F
from utils import alipay_ttsx



# Create your views here.
@login_required
def place(request):
    # 1 接收用户地址
    sku_ids = request.GET.getlist('sku_id')
    # 2 查询用户地址
    addr_list = request.user.address_set.all()
    # 3查询商品信息
    sku_list = []
    redis_client = get_redis_connection()
    key = 'cart%d' % request.user.id
    for sku_id in sku_ids:
        sku = GoodsSKU.objects.get(pk=sku_id)
        sku.cart_count = int(redis_client.hget(key, sku_id))
        sku_list.append(sku)

    context = {
        'title': '商品订单',
        'addr_list': addr_list,
        'sku_list': sku_list,
    }
    return render(request, 'place_order.html', context)


@login_required
@transaction.atomic
def handle(request):
    # 判断 是否为POST请求

    if request.method != 'POST':
        return Http404

    # 获取数据
    dict = request.POST
    addr_id = dict.get('addr_id')
    pay_style = dict.get('pay_style')
    sku_ids = dict.get('sku_ids')

    # 判断数据的有效性
    if not all([addr_id, pay_style, sku_ids]):
        return JsonResponse({'status': 2})
    # 事物开启
    sid = transaction.savepoint()

    # 查看库存 获取数据
    order_info = OrderInfo()
    order_info.order_id = str(uuid.uuid1())
    order_info.user = request.user
    order_info.address_id = int(addr_id)
    order_info.total_count = 0
    order_info.total_amount = 0
    order_info.trans_cost = 10
    order_info.pay_method = int(pay_style)
    order_info.save()

    redis_client = get_redis_connection()
    key = 'cart%d' % request.user.id

    is_ok = True
    sku_ids = sku_ids.split(',')
    sku_ids.pop()
    total_count = 0
    total_amount = 0
    for sku_id in sku_ids:
        sku = GoodsSKU.objects.get(pk=sku_id)
        cart_count = int(redis_client.hget(key, sku_id))
        result = GoodsSKU.objects.filter(pk=sku_id, stock__gte=cart_count).update(stock=F('stock') - cart_count, sales=F('sales') + cart_count)
        # 库存充足则 减少库存 增加销量
        if result:
            order_goods = OrderGoods()
            order_goods.order = order_info
            order_goods.sku = sku
            order_goods.count = cart_count
            order_goods.price = sku.price
            order_goods.save()
            # 3.4计算总价、总数量
            total_count += cart_count
            total_amount += sku.price * cart_count

        # 库存不足 则返回 订单页
        else:
            is_ok = False
            break
    if is_ok:
        # 保存总数量、总价
        order_info.total_count = total_count
        order_info.total_amount = total_amount
        order_info.save()

        transaction.savepoint_commit(sid)
        # 删除购物车数据
        for sku_id in sku_ids:
            redis_client.hdel(key, sku_id)

        return JsonResponse({'status': 1})
    else:
        transaction.savepoint_rollback(sid)

        return JsonResponse({'status': 3})

def pay(request):
    order_id = request.GET.get('order_id')
    order = OrderInfo.objects.get(pk=order_id)
    total = order.total_amount
    url = alipay_ttsx.pay(order_id, total)
    return JsonResponse({'status': 1, 'url': url})


def query(request):
    order_id = request.POST.get('order_id')
    if alipay_ttsx.query(order_id):
        order = OrderInfo.objects.get(pk=order_id)
        order.status = 2
        order.save()
        return JsonResponse({'status': 1})
    else:
        return JsonResponse({'status': 2})
