from datetime import datetime, timedelta, timezone

from time import time
from django.http import JsonResponse
from django.shortcuts import render

from web import models
from web.forms.project import ProjectForm

from utils.tecent.cos import creat_bucket

def project_list(request):
    """项目列表"""
    # 在中间间中把价格策略写进了request
    if request.method == 'GET':
        # 查看项目列表
        """
        每次查看项目列表应该都要检查和更新状态
        """
        # 获取现在的时间
        now_time = datetime.now()
        # 获取每个药的时间遍历
        medicines_list = models.Medicine.objects.filter(creator=request.People.user)
        # 我参与的
        for row in models.ProjectUser.objects.filter(participter=request.People.user):
            medicines_list += row.task
        # 获取每个obj
        for row in medicines_list:
            # 处理时间字符串,转换为无时区的
            expiry_date = row.expiry_date.replace(tzinfo=None)
            if now_time + timedelta(days=20) >= expiry_date and now_time + timedelta(days=20) < expiry_date:
                models.Medicine.objects.filter(id=row.id).update(status=2, color=3)
            elif now_time > expiry_date:
                models.Medicine.objects.filter(id=row.id).update(status=3, color=1)
            else:
                models.Medicine.objects.filter(id=row.id).update(status=1, color=2)

        """
               1. 从数据库中获取两部分数据
                   我创建的所有项目：所有药品状态
                   我参与管理的所有项目：所有药品状态
               2. 提取已星标
                   列表 = 循环 [我创建的所有项目] + [我参与的所有项目] 把已星标的数据提取

               得到三个列表：星标、创建、参与
        """
        # 遍历过后加入到各自的地方
        medicine_dict = {'临期': [], '过期': [], '正常': [], 'my': [], 'join': []}

        # 我创建的所有项目：所有药品状态
        my_medicine_list = models.Medicine.objects.filter(creator=request.People.user)

        for row in my_medicine_list:
            medicine_dict['my'].append(row)
            if row.status == 2:
                medicine_dict['临期'].append(row)
            elif row.status == 3:
                medicine_dict['过期'].append(row)
            else:
                medicine_dict['正常'].append(row)

        # 我参与管理的所有项目：所有药品状态
        join_projects_list = models.ProjectUser.objects.filter(participter=request.People.user)
        for row in join_projects_list:
            medicine_dict['join'].append(row.task)
            if row.task.status == 2:
                medicine_dict['临期'].append(row.task)  # 这个task是指整个一条的medicine数据
        form = ProjectForm(request)
        return render(request, 'web/project_list.html', {'form': form, 'medicine_dict': medicine_dict})
    # POST,对话框的ajax添加项目
    form = ProjectForm(request, data=request.POST)
    if form.is_valid():
        # 为项目创建一个桶
        # "{手机号}-{时间戳}--167868"
        bucekt="{}-{}-1325585694".format(request.People.user.mobile_phone,str(int(time())*1000),)
        region = "ap-chengdu"
        creat_bucket(bucekt, region)
        # 把桶和区域写入数据库
        form.instance.bucket = bucekt
        form.instance.region = region
        # 验证通过
        form.instance.creator = request.People.user
        # 处理过期时间

        # 获取存储时间
        warehousing_time = datetime.now()
        # 获取保质期
        EXP = form.cleaned_data['EXP']
        expiry_date = (warehousing_time + timedelta(days=EXP * 30)).astimezone(timezone.utc)
        form.instance.expiry_date = expiry_date
        # 创建项目
        form.save()
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'error': form.errors})
