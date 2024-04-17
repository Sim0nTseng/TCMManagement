from django.db import models

# Create your models here.
class UserInfo(models.Model):
    username = models.CharField(max_length=32,verbose_name='用户名',db_index=True) #db_index是创建索引，以后根据这个查速度就会很快
    # 本质还是字符串
    email = models.EmailField(verbose_name='邮箱',max_length=32)
    mobile_phone = models.CharField(verbose_name='手机号',max_length=32)
    password = models.CharField(max_length=32,verbose_name='密码')