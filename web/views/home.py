import json

from django.http import HttpResponse
from django.shortcuts import render, redirect
import datetime

from django_redis import get_redis_connection

from TCMManagement import settings
from utils.alipay import AliPay
from utils.encrypt import uid
from web import models


def index(request):
    return render(request, 'web/index.html')


def logout(request):
    request.session.flush()
    return redirect('/index/')


def price(request):
    """套餐"""
    policy_list = models.Price.objects.filter(category=2)
    return render(request, 'web/price.html', {'policy_list': policy_list})


def payment(request, policy_id):
    """支付"""
    # 1.价格策略
    policy_object = models.Price.objects.filter(id=policy_id, category=2).first()
    if not policy_object:
        return redirect('price')
    # 2.需要购买的数量
    number = request.GET.get('number', "")
    if not number or not number.isdecimal():
        return redirect('price')
    number = int(number)
    if number < 1:
        return redirect('price')

    # 3.计算原价
    origin_price = number * policy_object.price

    # 4.之前购买过套餐
    balance = 0
    _object = None
    if request.People.price_policy.category == 2:
        # 找到之前的订单,总支付的费用，开始~结束时间，剩余天数=抵扣的钱
        _object = models.Transaction.objects.filter(user=request.People.user, status=2).order_by('-id').first()
        total_timedalta = _object.end_datetime - _object.start_datetime
        balance_timedalta = _object.end_datetime - datetime.datetime.now()
        if total_timedalta.days == balance_timedalta.days:
            balance = _object.price / total_timedalta.days * (balance_timedalta.days - 1)
        else:
            balance = _object.price / total_timedalta.days * balance_timedalta.days
    if balance >= origin_price:
        return redirect('price')

    context = {
        'policy_id': policy_object.id,
        'number': number,
        'origin_price': origin_price,
        'balance': round(balance, 2),
        'total_price': origin_price - round(balance, 2)
    }
    conn = get_redis_connection()
    key = "payment_{}".format(request.People.user.mobile_phone)
    conn.set(key, json.dumps(context), ex=60 * 30)
    context['policy_object'] = policy_object
    context['transaction'] = _object
    return render(request, 'web/payment.html', context)


def pay(request):
    conn = get_redis_connection()
    key = 'payment_{}'.format(request.People.user.mobile_phone)
    context_string = conn.get(key)
    if not context_string:
        return redirect('price')
    context = json.loads(context_string.decode('utf-8'))

    # 1. 数据库中生成交易记录（待支付）
    #     等支付成功之后，我们需要把订单的状态更新为已支付、开始&结束时间
    order_id = uid(request.People.user.mobile_phone)
    total_price = context['total_price']
    models.Transaction.objects.create(
        status=1,
        order=order_id,
        user=request.People.user,
        price_policy_id=context['policy_id'],
        count=context['number'],
        price=total_price
    )
    # 生成支付链接

    ali_pay = AliPay(
        appid=settings.ALI_APPID,
        app_notify_url=settings.ALI_NOTIFY_URL,
        return_url=settings.ALI_RETURN_URL,
        app_private_key_path=settings.ALI_PRI_KEY_PATH,
        alipay_public_key_path=settings.ALI_PUB_KEY_PATH
    )
    query_params = ali_pay.direct_pay(
        subject="会员支付",  # 商品简单描述
        out_trade_no=order_id,  # 商户订单号
        total_amount=total_price
    )
    pay_url = "{}?{}".format(settings.ALI_GATEWAY, query_params)
    return redirect(pay_url)


def pay_notify(request):
    """ 支付成功之后触发的URL """
    ali_pay = AliPay(
        appid=settings.ALI_APPID,
        app_notify_url=settings.ALI_NOTIFY_URL,
        return_url=settings.ALI_RETURN_URL,
        app_private_key_path=settings.ALI_PRI_KEY_PATH,
        alipay_public_key_path=settings.ALI_PUB_KEY_PATH
    )

    if request.method == 'GET':
        # 页面跳转是GET
        # 只做跳转，判断是否支付成功了，不做订单的状态更新。
        # 支付吧会讲订单号返回：获取订单ID，然后根据订单ID做状态更新 + 认证。
        # 支付宝公钥对支付给我返回的数据request.GET 进行检查，通过则表示这是支付宝返还的接口。
        params = request.GET.dict()
        sign = params.pop('sign', None)
        status = ali_pay.verify(params, sign)
        if status:
            """
            current_datetime = datetime.datetime.now()
            out_trade_no = params['out_trade_no']
            _object = models.Transaction.objects.filter(order=out_trade_no).first()

            _object.status = 2
            _object.start_datetime = current_datetime
            _object.end_datetime = current_datetime + datetime.timedelta(days=365 * _object.count)
            _object.save()
            """
            return HttpResponse('支付完成')
        return HttpResponse('支付失败')
    else:
        from urllib.parse import parse_qs
        body_str = request.body.decode('utf-8')
        post_data = parse_qs(body_str)
        post_dict = {}
        for k, v in post_data.items():
            post_dict[k] = v[0]

        sign = post_dict.pop('sign', None)
        status = ali_pay.verify(post_dict, sign)
        if status:
            current_datetime = datetime.datetime.now()
            out_trade_no = post_dict['out_trade_no']
            _object = models.Transaction.objects.filter(order=out_trade_no).first()

            _object.status = 2
            _object.start_datetime = current_datetime
            _object.end_datetime = current_datetime + datetime.timedelta(days=365 * _object.count)
            _object.save()
            return HttpResponse('success')

        return HttpResponse('error')
