"""
用户注册相关功能：注册，短信，登录，注销
"""
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from web.forms import account

def register(request):
    """注册"""
    if request.method=="GET":
        register_form=account.registerModelform()
        return render(request, 'web/register.html',{'form':register_form})
    #数据校验惹
    form=account.registerModelform(data=request.POST)
    if form.is_valid():
        # 验证通过，写入数据库（密码是密文）
        form.save() #save保存的话他会剔除一下不用的字段，只保留数据库要的
        return JsonResponse({'status':True,'data':'/login/'})
    else:
        return JsonResponse({'status':False,'error':form.errors}) #转去写钩子惹

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
