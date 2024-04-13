import json

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.conf import settings
from django_redis import get_redis_connection

from utils.tecent.sms import smsSendMessage
from web import models
import random


# Create your views here.
class registerModelform(forms.ModelForm):
    mobile_phone=forms.CharField(label="手机号",validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9]}\d{9}$','手机号错误'),])
    password=forms.CharField(label="密码",widget=forms.PasswordInput())
    confirm_password = forms.CharField(label="确认密码", widget=forms.PasswordInput(render_value=True))  # 这一句话加上就不会清空了
    code=forms.CharField(label="验证码",widget=forms.TextInput())
    class Meta:
        model = models.UserInfo
        fields = ['username', 'email','password', 'confirm_password','mobile_phone', 'code']

    def __init__(self,*args,**kwargs):
        # 相当又写了一编但是没变化
        super().__init__(*args,**kwargs)
        for name,field in self.fields.items():
            field.widget.attrs['class']='form-control'
            field.widget.attrs['placeholder']=f"请输入{field.label}"

class SendSmsForm(forms.Form):
    # 只是为了做校验
    mobile_phone=forms.CharField(label='手机号',validators=[RegexValidator(r'^1[3-9]\d{9}$','手机号格式错误')])

    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request=request

    def clean_mobile_phone(self):
        """手机号校验的钩子"""
        mobile_phone=str(self.cleaned_data['mobile_phone'])
        # 判断短信模板是否有问题
        #思路：我们要从request。GET(”tpl")获取tpl来校验是否有这个模板好报错
        #肯定写在一个钩子中比较好
        #但是这里面没有request，我们就给他传过来，
        #使用init方法，让他自己含有
        tpl=self.request.GET.get('tpl')
        template_id=settings.TENCENT_SMS_TEMPLATE.get(tpl)
        print(template_id)

        if not template_id:
            raise ValidationError("滚啊死爬虫")


        #校验数据库中是否已有手机号
        exists=models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exists:
            raise ValidationError("改手机号已注册")
        #发短信&写redis
        code=str(random.randrange(1000,9999))

        #发送短信
        sms=smsSendMessage(mobile_phone,template_id,code)
        data = json.loads(sms)
        print(data['SendStatusSet'][0]['Message'])
        if data['SendStatusSet'][0]['Message']!="send success":
            raise ValidationError("发生未知错误")


        #验证码写入redis（django-redis）
        conn=get_redis_connection()
        conn.set(mobile_phone,code,ex=60)

        return mobile_phone