import datetime

from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

from TCMManagement import settings
from web import models


class TCMAdmin(object):
    def __init__(self):
        self.user = None
        self.price_policy = None


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """如果用户已登录，则在request中赋值"""
        Admin = TCMAdmin()

        user_id = request.session.get('user_id', 0)
        user_object = models.UserInfo.objects.filter(id=user_id).first()
        Admin.user = user_object
        request.People = Admin

        # 白名单，没有登陆也可以访问的URL（settings中加）
        """
        1.获取当前用户访问的URL
        2.检查URL是否在白名单中，如果在则可以继续访问，如果不在则进行判断是否登录
        """

        if request.path_info in settings.WHITE_REGEX_URL_LIST:
            return

        # 检查用户是否已登录，已登录继续往后走，未登录则放回登陆界面
        if not request.People.user:
            return redirect('/login/')

            # 登陆成功之后，访问后台管理时，获取当前用户所拥有的额度
            # 方式一：免费额度在交易记录中存储
            # 获取当前用户ID值最大（最近交易记录）
        _object = models.Transaction.objects.filter(user=user_object, status=2).order_by('-id').first()
        # 判断是否已过期
        curent_datetime = datetime.datetime.now()
        # 判断是否存在且小于结束时间，因为如果是免费版的，endtime为0
        if _object.end_datetime and _object.end_datetime < curent_datetime:
            # 获取免费版，将其变为免费版
            _object = models.Transaction.objects.filter(user=user_object, status=2, price_policy__category=1).first()
        # request.transaction = _object
        Admin.price_policy = _object.price_policy
        request.People = Admin
        # 方式二：免费额度存储配置文件
