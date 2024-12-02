import json

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.conf import settings
from django_redis import get_redis_connection

from utils import encrypt
from utils.tecent.sms import smsSendMessage
from web import models
import random


# Create your views here.
class registerModelform(forms.ModelForm):
    mobile_phone = forms.CharField(label="手机号",
                                   validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号错误'), ])
    password = forms.CharField(
        label="密码",
        max_length=64,
        min_length=8,
        error_messages={
            'min_length': '密码不能小于8个字符',
            'max_length': '密码不能大于64个字符'
        },
        widget=forms.PasswordInput())
    confirm_password = forms.CharField(label="确认密码", widget=forms.PasswordInput(render_value=True))  # 这一句话加上就不会清空了
    # code = forms.CharField(label="验证码", widget=forms.TextInput())

    class Meta:
        model = models.UserInfo
        # fields = ['username', 'email', 'password', 'confirm_password', 'mobile_phone', 'code']
        fields = ['username', 'email', 'password', 'confirm_password', 'mobile_phone', ]

    def __init__(self, *args, **kwargs):
        # 相当又写了一编但是没变化
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = f"请输入{field.label}"

    def clean_username(self):
        # 写了和没写一样
        username = self.cleaned_data['username']
        exists = models.UserInfo.objects.filter(username=username).exists()
        if exists:
            raise ValidationError("喵喵喵，用户名已存在")
        return username

    # def clean_email(self):
    #     # 写了和没写一样
    #     email = self.cleaned_data['email']
    #     exists = models.UserInfo.objects.filter(email=email).exists()
    #     if exists:
    #         raise ValidationError("喵喵喵，该邮箱已存注册")
    #     return email

    def clean_password(self):
        pwd = self.cleaned_data['password']
        # 加密&返回
        pwd = encrypt.md5(pwd)
        return pwd

    def clean_confirm_password(self):
        # 因为confirm_password在后面所以是可以用self得到password的！！！！！！先后顺序
        pwd = self.cleaned_data.get('password')
        confirm_password = encrypt.md5(self.cleaned_data['confirm_password'])
        if pwd != confirm_password:
            raise ValidationError("前后密码不一致")
        return confirm_password

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exists:
            raise ValidationError("该手机号已注册")
        return mobile_phone

    # def clean_code(self):
    #     code = self.cleaned_data['code']
    #     mobile_phone = self.cleaned_data.get('mobile_phone')
    #     if not mobile_phone:
    #         return code
    #     conn = get_redis_connection()
    #     print(mobile_phone)
    #     redis_code = conn.get(mobile_phone)
    #     if not redis_code:
    #         raise ValidationError("验证码失效或未发送，请重试，喵喵")
    #     # 从redis中得到的是比特类型的数据，要给他解码
    #     redis_str_code = redis_code.decode('utf-8')
    #     # 加个strip去除左右两边的空格
    #     if code.strip() != redis_str_code:
    #         raise ValidationError("验证码错误")


class SendSmsForm(forms.Form):
    # 只是为了做校验
    mobile_phone = forms.CharField(label='手机号', validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号格式错误')])

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_mobile_phone(self):
        """手机号校验的钩子"""
        mobile_phone = str(self.cleaned_data['mobile_phone'])
        # 判断短信模板是否有问题
        # 思路：我们要从request。GET(”tpl")获取tpl来校验是否有这个模板好报错
        # 肯定写在一个钩子中比较好
        # 但是这里面没有request，我们就给他传过来，
        # 使用init方法，让他自己含有
        # 发短信&写redis
        code = str(random.randrange(10000, 99999))
        tpl = self.request.GET.get('tpl')
        template_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
        # 校验数据库中是否已有手机号
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        print(exists,tpl)
        if tpl=="login":
            if not exists:
                raise ValidationError("该手机号未被注册")
        else:   #rigister的校验
            if exists:
                raise ValidationError("改手机号已注册")
            if not template_id:
                raise ValidationError("滚啊死爬虫")

        # 发送短信
        if tpl=='login':
           sms = smsSendMessage(mobile_phone, template_id, [code,'1'])
        else:
           sms = smsSendMessage(mobile_phone, template_id,[code])
        data = json.loads(sms)
        #
        if data['SendStatusSet'][0]['Message'] != "send success":
           raise ValidationError("发生未知错误")
        try:
            # 验证码写入redis（django-redis）
            conn = get_redis_connection()
            conn.set(mobile_phone, code, ex=60)


        except Exception:
            raise ValidationError("验证码已失效或错误")

        return mobile_phone

class BootstrapForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # 相当又写了一编但是没变化
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = f"请输入{field.label}"

class LoginSMSForm(BootstrapForm,forms.Form):
    mobile_phone = forms.CharField(label="手机号",
                                   validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号错误'), ])
    code = forms.CharField(label="验证码", widget=forms.TextInput())

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        user_obj=models.UserInfo.objects.filter(mobile_phone=mobile_phone).first()
        if not user_obj:
            raise ValidationError("手机号不存在")
        # 省事，好写session
        return user_obj
    def clean_code(self):
        code = self.cleaned_data['code']
        user_obj = self.cleaned_data['mobile_phone']
        # 手机号不存在无序校验
        if not user_obj:
            return code
        conn = get_redis_connection()
        redis_code = conn.get(user_obj)
        if not redis_code:
            raise ValidationError("验证码失效或未发送，请重试，喵喵")
        # 从redis中得到的是比特类型的数据，要给他解码
        redis_str_code = redis_code.decode('utf-8')
        # 加个strip去除左右两边的空格
        if code.strip() != redis_str_code:
            raise ValidationError("验证码错误")
        return code


class LoginForm(BootstrapForm,forms.Form):
    username = forms.CharField(label="邮箱或手机号")
    password = forms.CharField(label="密码",widget=forms.PasswordInput(render_value=True))
    code=forms.CharField(label='图片验证码')

    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request =request

    def clean_password(self):
        pwd = self.cleaned_data['password']
        #加密&返回
        return encrypt.md5(pwd)
    def clean_code(self):
        """钩子"""
        #1.读取用户输入的验证码
        code=self.cleaned_data['code']

        #去session_code获取自己的验证码
        session_code=self.request.session.get('image_code')
        if not session_code:
            raise ValidationError("验证码已过期，请重新获取")
        if code.strip().upper() != session_code.strip().upper():
            raise ValidationError("验证码错误")
        return code