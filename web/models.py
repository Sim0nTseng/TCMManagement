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
    project_space = models.PositiveIntegerField(verbose_name="单项目空间", help_text="G")
    per_file_size = models.PositiveIntegerField(verbose_name="单文件大小", help_text="M")

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


# 药品表
class Medicine(models.Model):
    COLOR_CHOICES = (
        (1, "#FF0000"),  # 56b8eb 红色
        (2, "#98FB98"),  # f28033 绿色
        (3, "#FFB90F"),  # ebc656 黄色
    )

    STATUS_CHOICES = (
        (1, "正常"),
        (2, "临期"),
        (3, "过期")
    )

    sava_mothod = (
        (1, "常温保存"),
        (2, "干燥保存"),
        (3, "高湿度保存"),
        (4, "冷藏")
    )

    bucket = models.CharField(verbose_name="COS桶", max_length=128)
    region = models.CharField(verbose_name="COS区域", max_length=32)

    use_space = models.BigIntegerField(verbose_name="该药品COS已使用空间", default=0, help_text='字节')
    # 项目已使用的管理药品数
    use_medicine = models.IntegerField(verbose_name="已使用管理药品数", default=0)
    name = models.CharField(max_length=32, verbose_name='药品名称', db_index=True)
    color = models.SmallIntegerField(verbose_name="颜色", choices=COLOR_CHOICES, default=1)
    status = models.SmallIntegerField(verbose_name='药品状态', choices=STATUS_CHOICES, default=1)
    # 药品描述
    desc = models.CharField(verbose_name="药品描述", max_length=255, blank=True, null=True)
    # 保质期,以月份存储
    EXP = models.IntegerField(verbose_name='保质期')
    # 干湿保存方法
    keep = models.SmallIntegerField(verbose_name='保存方法', choices=sava_mothod, default=1)
    # 入库时间
    warehousing_time = models.DateTimeField(verbose_name='入库时间', auto_now_add=True)
    # 过期时间
    expiry_date = models.DateTimeField(verbose_name='过期时间')
    # 库存
    stocks = models.IntegerField(verbose_name='库存（Kg）')
    # 余量
    # margin=models.IntegerField(verbose_name='余量（Kg）')
    # 记录人
    creator = models.ForeignKey(verbose_name='记录人', to="UserInfo", on_delete=models.CASCADE, null=True, blank=True)
    # 创建时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")


# 药品管理员
class ProjectUser(models.Model):
    """药品管理添加者"""
    participter = models.ForeignKey(verbose_name="任务参与者", to="UserInfo", on_delete=models.CASCADE)
    # 传入一整条 object，是不行的，必须传入一条数据
    task = models.ForeignKey(verbose_name="药品任务", to='Medicine', on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="加入时间")


class Wiki(models.Model):
    """wiki文章"""
    medicine = models.ForeignKey(verbose_name="药品", to="Medicine", on_delete=models.CASCADE)
    title = models.CharField(max_length=32, verbose_name="标题")
    content = models.TextField(verbose_name="内容/回复")
    depth = models.IntegerField(verbose_name="深度", default=1)
    # 要做子关联
    parent = models.ForeignKey(verbose_name="上级任务", to="Wiki", on_delete=models.CASCADE, null=True, blank=True,
                               related_name="children", default=None)


class File(models.Model):
    """文件"""
    medicine = models.ForeignKey(verbose_name="药品", to="Medicine", on_delete=models.CASCADE)
    file_type_choices = (
        (1, "文件"),
        (2, "文件夹"),
    )
    file_type = models.SmallIntegerField(verbose_name="类型", choices=file_type_choices)
    name = models.CharField(verbose_name="文件夹名称", max_length=32, help_text="文件/文件夹名")
    key = models.CharField(verbose_name="文件存储在COS中的key", max_length=128, null=True, blank=True)
    #
    file_size = models.BigIntegerField(verbose_name="文件大小", null=True, blank=True, help_text='字节')
    file_path = models.CharField(verbose_name="文件路径", max_length=255, null=True, blank=True)
    parent = models.ForeignKey(verbose_name="父级目录", to="self", related_name='child', null=True, blank=True,
                               on_delete=models.CASCADE)
    create_datetime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_user = models.ForeignKey(verbose_name="最近更新者", to="UserInfo", on_delete=models.CASCADE)
    update_datetime = models.DateTimeField(auto_now=True, verbose_name="更新时间")


class Issues(models.Model):
    """ 问题 """
    project = models.ForeignKey(verbose_name='药品', to='Medicine', on_delete=models.CASCADE)
    issues_type = models.ForeignKey(verbose_name='问题类型', to='IssuesType', on_delete=models.CASCADE)
    module = models.ForeignKey(verbose_name='模块', to='Module', null=True, blank=True, on_delete=models.CASCADE)

    subject = models.CharField(verbose_name='主题', max_length=80)
    desc = models.TextField(verbose_name='问题描述')
    priority_choices = (
        ("danger", "高"),
        ("warning", "中"),
        ("success", "低"),
    )
    priority = models.CharField(verbose_name='优先级', max_length=12, choices=priority_choices, default='danger')

    # 新建、处理中、已解决、已忽略、待反馈、已关闭、重新打开
    status_choices = (
        (1, '新建'),
        (2, '处理中'),
        (3, '已解决'),
        (4, '已忽略'),
        (5, '待反馈'),
        (6, '已关闭'),
        (7, '重新打开'),
    )
    status = models.SmallIntegerField(verbose_name='状态', choices=status_choices, default=1)

    assign = models.ForeignKey(verbose_name='指派', to='UserInfo', related_name='task', null=True, blank=True,
                               on_delete=models.CASCADE)
    attention = models.ManyToManyField(verbose_name='关注者', to='UserInfo', related_name='observe', blank=True)

    start_date = models.DateField(verbose_name='开始时间', null=True, blank=True)
    end_date = models.DateField(verbose_name='结束时间', null=True, blank=True)
    mode_choices = (
        (1, '公开模式'),
        (2, '隐私模式'),
    )
    mode = models.SmallIntegerField(verbose_name='模式', choices=mode_choices, default=1)

    parent = models.ForeignKey(verbose_name='父问题', to='self', related_name='child', null=True, blank=True,
                               on_delete=models.SET_NULL)

    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', related_name='create_problems',
                                on_delete=models.CASCADE)

    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    latest_update_datetime = models.DateTimeField(verbose_name='最后更新时间', auto_now=True)

    def __str__(self):
        return self.subject


class Module(models.Model):
    """ 模块（里程碑）"""
    project = models.ForeignKey(verbose_name='药品', to='Medicine', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='模块名称', max_length=32)

    def __str__(self):
        return self.title


class IssuesType(models.Model):
    """ 问题类型 例如：任务、功能、Bug """
    PROJECT_INIT_LIST = ["物流", "售后", "工作"]

    title = models.CharField(verbose_name='类型名称', max_length=32)
    project = models.ForeignKey(verbose_name='药品', to='Medicine', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class IssuesReply(models.Model):
    """ 问题回复"""

    reply_type_choices = (
        (1, '修改记录'),
        (2, '回复')
    )
    reply_type = models.IntegerField(verbose_name='类型', choices=reply_type_choices)

    issues = models.ForeignKey(verbose_name='问题', to='Issues', on_delete=models.CASCADE)
    content = models.TextField(verbose_name='描述')
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', related_name='create_reply',
                                on_delete=models.CASCADE)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    reply = models.ForeignKey(verbose_name='回复', to='self', null=True, blank=True, on_delete=models.CASCADE)


class ProjectInvite(models.Model):
    """ 项目邀请码 """
    project = models.ForeignKey(verbose_name='项目', to='Medicine', on_delete=models.CASCADE)
    code = models.CharField(verbose_name='邀请码', max_length=64, unique=True)
    count = models.PositiveIntegerField(verbose_name='限制数量', null=True, blank=True, help_text='空表示无数量限制')
    use_count = models.PositiveIntegerField(verbose_name='已邀请数量', default=0)
    period_choices = (
        (30, '30分钟'),
        (60, '1小时'),
        (300, '5小时'),
        (1440, '24小时'),
    )
    period = models.IntegerField(verbose_name='有效期', choices=period_choices, default=1440)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', related_name='create_invite', on_delete=models.CASCADE)
