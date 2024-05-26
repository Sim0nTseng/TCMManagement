
from django.db import models


# Create your models here.
# 用户表
class UserInfo(models.Model):
    username = models.CharField(max_length=32, verbose_name='用户名', db_index=True)  # db_index是创建索引，以后根据这个查速度就会很快
    # 本质还是字符串
    email = models.EmailField(verbose_name='邮箱', max_length=32)
    mobile_phone = models.CharField(verbose_name='手机号', max_length=32)
    password = models.CharField(max_length=32, verbose_name='密码')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    # price_policy=models.ForeignKey(verbose_name='价格策略',to='Price',null=True,blank=True,on_delete=models.CASCADE)


# 价格策略表
class Price(models.Model):
    category_choices = (
        (1, "Free"),
        (2, "VIP"),
        (3, "SVIP")
    )
    # 价格政策
    price_choices = (
        (1, 0),
        (2, 199),
        (3, 299)
    )
    title = models.CharField(max_length=128, verbose_name='标题', null=True)
    category = models.SmallIntegerField(verbose_name='用户级别', choices=category_choices, default=1)
    price = models.SmallIntegerField(verbose_name='价格', choices=price_choices, default=1)

    project_num = models.PositiveIntegerField(verbose_name="项目数")
    project_member = models.PositiveIntegerField(verbose_name="项目成员数")

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")


# 交易记录表
class Transaction(models.Model):
    """交易记录"""
    status_choice = (
        (1, "未支付"),
        (2, "已支付")
    )
    status = models.SmallIntegerField(verbose_name="状态", choices=status_choice, default=1)

    order = models.CharField(verbose_name="订单号", max_length=64, unique=True)
    user = models.ForeignKey(verbose_name="用户", to="UserInfo", on_delete=models.CASCADE)
    price_policy = models.ForeignKey(verbose_name="价格策略", to="Price", on_delete=models.CASCADE)

    count = models.IntegerField(verbose_name="数量（年）", help_text='0表示无限期')
    price = models.IntegerField(verbose_name="实际支付费用")

    start_datetime = models.DateTimeField(verbose_name="开始时间", null=True, blank=True)
    end_datetime = models.DateTimeField(verbose_name="结束时间", null=True, blank=True)

    create_datetime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")


#药品表
class Medicine(models.Model):

    COLOR_CHOICES = (
        (1, "#56b8eb"),  # 56b8eb
        (2, "#f28033"),  # f28033
        (3, "#ebc656"),  # ebc656
        (4, "#a2d148"),  # a2d148
        (5, "#20BFA4"),  # #20BFA4
        (6, "#7461c2"),  # 7461c2,
        (7, "#20bfa3"),  # 20bfa3,
    )

    STATUS_CHOICES = (
        (1,"正常"),
        (2,"临期"),
        (3,"过期")
    )

    sava_mothod=(
        (1,"常温保存"),
        (2,"干燥保存"),
        (3,"高湿度保存"),
        (4,"冷藏")
    )

    #项目已使用的管理药品数
    use_medicine=models.IntegerField(verbose_name="已使用管理药品数",default=0)
    name = models.CharField(max_length=32,verbose_name='药品名称',db_index=True)
    color=models.SmallIntegerField(verbose_name="颜色",choices=COLOR_CHOICES,default=1)
    status=models.SmallIntegerField(verbose_name='药品状态',choices=STATUS_CHOICES,default=1)
    #药品描述
    desc=models.CharField(verbose_name="药品描述",max_length=255,blank=True,null=True)
    #保质期,以月份存储
    EXP=models.IntegerField(verbose_name='保质期')
    #干湿保存方法
    keep=models.SmallIntegerField(verbose_name='保存方法',choices=sava_mothod,default=1)
    #入库时间
    warehousing_time=models.DateTimeField(verbose_name='入库时间',auto_now_add=True)
    # 过期时间
    expiry_date=models.DateTimeField(verbose_name='过期时间')
    #库存
    stocks=models.IntegerField(verbose_name='库存（Kg）')
    #余量
    # margin=models.IntegerField(verbose_name='余量（Kg）')
    #记录人
    creator=models.ForeignKey(verbose_name='记录人',to="UserInfo",on_delete=models.CASCADE,null=True,blank=True)
    #创建时间
    create_time=models.DateTimeField(auto_now_add=True,verbose_name="创建时间")


# 药品管理员
class ProjectUser(models.Model):
    """药品管理添加者"""
    participter = models.ForeignKey(verbose_name="任务参与者", to="UserInfo", on_delete=models.CASCADE)
    # 传入一整条 object
    task = models.ForeignKey(verbose_name="药品任务", to='Medicine', on_delete=models.CASCADE)

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="加入时间")
