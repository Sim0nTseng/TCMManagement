"""
用户注册相关功能：注册，短信，登录，注销
"""
import datetime
from io import BytesIO
import uuid

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from utils.image_code import check_code
from web import models

from web.forms import account
from django.db.models import Q

def register(request):
    """注册"""
    if request.method == "GET":
        register_form = account.registerModelform()
        return render(request, 'web/register.html', {'form': register_form})
    # 数据校验惹
    form = account.registerModelform(data=request.POST)
    if form.is_valid():
        # 验证通过，写入数据库（密码是密文）
        instance=form.save()  # save保存的话他会剔除一下不用的字段，只保留数据库要的
        # instance,在数据库中新增一条数据，并将新增的这条数据赋值给instance
        policy_obj=models.Price.objects.filter(category=1,title="个人免费版").first()
        #创建交易记录(免费版)
        models.Transaction.objects.create(
            status=2,
            order=str(uuid.uuid4()),
            #就是给数据给他
            user=instance,
            # 因为是和price表关联的，所以要导入一下
            #就有价格策略了
            price_policy=policy_obj,
            count = 0,
            price = 0,
            start_datetime = datetime.datetime.now(),
        )

        return JsonResponse({'status': True, 'data': '/login/'})
    else:
        return JsonResponse({'status': False, 'error': form.errors})  # 转去写钩子惹


def send_sms(request):
    """发送短信"""
    form = account.SendSmsForm(request, data=request.GET)
    # 只是校验手机号不能为空，格式是否正确
    if form.is_valid():
        # 发短信
        # 写redis
        # 为了方便还是写在form里面
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'errors': form.errors})


def login_sms(request):
    """短信登陆"""
    if request.method == "GET":
        form=account.LoginSMSForm()
        return render(request, 'web/login_sms.html',{'form':form})
    form=account.LoginSMSForm(data=request.POST)    #获得数据
    # 数据校验喵喵喵
    if form.is_valid():
        mobile_phone=form.cleaned_data['mobile_phone']
        # 将用户信息写入session
        user_obj=models.UserInfo.objects.filter(mobile_phone=mobile_phone).first()
        request.session['user_id']=user_obj.id
        return JsonResponse({'status':True, 'data': '/index/'})
    else:
        return JsonResponse({'status': False, 'error': form.errors})


def login(request):
    """用户名和密码登录"""
    # 是post的提交方法,表单验证
    if request.method == "GET":
        form = account.LoginForm(request)
        return render(request, 'web/login.html', {'form': form})
    form=account.LoginForm(request,data=request.POST)
    if form.is_valid():
        username=form.cleaned_data['username']
        password=form.cleaned_data['password']

            # user_object=models.UserInfo.objects.filter(username=username,password=password).first()
            # （手机=username and pwd=pwd） or （邮箱=username and pwd=pwd）
            # 牛逼方法用Q,密码和手机必须成一个，密码必须成
        user_object = models.UserInfo.objects.filter(Q(email=username)|Q(mobile_phone=username)).filter(password=password).first()
        if user_object:
            # 用户名密码正确，登陆成功
            request.session['user_id'] = user_object.id
            request.session.set_expiry(60*60*24*14)
            return redirect('/project/list/')
        form.add_error('username','用户名和密码错误')
    return render(request,'web/login.html',{'form':form})


def image_code(request):
    """生成图片验证码"""
    # 调用pillow函数，生成图片
    img,code_str=check_code()
    # print(code_str)
    # 写入到自己的session中（以便后续获取验证码在进行校验）
    request.session['image_code'] = code_str
    # 给session设置60s超时,主动修改session的过期时间60s
    request.session.set_expiry(60)

    stream=BytesIO()
    img.save(stream, 'png')
    stream.getvalue()
    return HttpResponse(stream.getvalue())