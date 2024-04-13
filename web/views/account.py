"""
用户注册相关功能：注册，短信，登录，注销
"""
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from web.forms import account

def register(request):
    """注册"""
    register_form=account.registerModelform()
    return render(request, 'web/register.html',{'form':register_form})


def send_sms(request):
    """发送短信"""
    form=account.SendSmsForm(request,data=request.GET)
    # 只是校验手机号不能为空，格式是否正确
    if form.is_valid():
        #发短信
        #写redis
        # 为了方便还是写在form里面
        return JsonResponse({'status':True})
    return JsonResponse({'status':False,'errors':form.errors})
