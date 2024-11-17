
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
        (1, "#FF0000"),  # 56b8eb 红色
        (2, "#98FB98"),  # f28033 绿色
        (3, "#FFB90F"),  # ebc656 黄色
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

    bucket=models.CharField(verbose_name="COS桶", max_length=128)
    region=models.CharField(verbose_name="COS区域", max_length=32)

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

class Wiki(models.Model):
    """wiki文章"""
    medicine = models.ForeignKey(verbose_name="药品",to="Medicine", on_delete=models.CASCADE)
    title = models.CharField(max_length=32, verbose_name="标题")
    content = models.TextField(verbose_name="内容/回复")
    depth=models.IntegerField(verbose_name="深度",default=1)
    # 要做子关联
    parent=models.ForeignKey(verbose_name="上级任务",to="Wiki",on_delete=models.CASCADE,null=True,blank=True,related_name="children",default=None)



class File(models.Model):
    """文件"""
    medicine = models.ForeignKey(verbose_name="药品", to="Medicine", on_delete=models.CASCADE)
    file_type_choices = (
        (1, "文件"),
        (2, "文件夹"),
    )
    file_type = models.SmallIntegerField(verbose_name="类型", choices=file_type_choices)
    name = models.CharField(verbose_name="文件夹名称", max_length=32,help_text="文件/文件夹名")
    key=models.CharField(verbose_name="文件存储在COS中的key",max_length=128,null=True,blank=True)
    file_size=models.IntegerField(verbose_name="文件大小",null=True,blank=True)
    file_path = models.CharField(verbose_name="文件路径", max_length=255,null=True,blank=True)
    parent = models.ForeignKey(verbose_name="父级目录", to="self", related_name='child',null=True, blank=True,on_delete=models.CASCADE)
    create_datetime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_user=models.ForeignKey(verbose_name="最近更新者", to="UserInfo",on_delete=models.CASCADE)
    update_datetime = models.DateTimeField(auto_now=True, verbose_name="更新时间")