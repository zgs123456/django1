from alipay import AliPay
from django.conf import settings


def create_alipay():
    # 验签：验证核实商家身份
    alipay = AliPay(
        appid=settings.APP_ID,
        app_notify_url=None,
        alipay_public_key_path=settings.ALIPAY_PUBLIC_KEY,
        app_private_key_path=settings.APP_PRIVATE_KEY,
        sign_type="RSA2",
        # 如果使用沙箱环境，则设置成True
        # 如果使用正式环境，则设置成False
        debug=True
    )
    return alipay


def pay(order_id, total):
    alipay = create_alipay()
    # 请求支付alipay.trade.page.pay
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order_id,
        total_amount=str(total),
        subject='天天生鲜 订单支付',
        return_url=None,
        notify_url=None
    )
    return settings.ALIPAY_GATEWAY + order_string


def query(order_id):
    alipay = create_alipay()
    #查询支付是否成功
    result = alipay.api_alipay_trade_query(out_trade_no=order_id)
    if result.get('code') == '10000' and result.get('trade_status') == 'TRADE_SUCCESS':
        return True
    else:
        return False
