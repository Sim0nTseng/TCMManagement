from datetime import datetime, timedelta, timezone
from django.db.models import QuerySet

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
        projects_list = models.Project.objects.filter(creator=request.People.user)
        join_list = models.ProjectUser.objects.filter(participter=request.People.user)
        related_projects = []
        related_projects.append(projects_list)
        for queryset in join_list:
            related_projects.append(queryset.task)

        # 获取每个obj
        for row in projects_list:
            # 处理时间字符串,转换为无时区的
            expiry_date = row.expiry_date.replace(tzinfo=None)
            if now_time + timedelta(days=20) >= expiry_date and now_time + timedelta(days=20) < expiry_date:
                models.Project.objects.filter(id=row.id).update(status=2, color=3)
            elif now_time > expiry_date:
                models.Project.objects.filter(id=row.id).update(status=3, color=1)
            else:
                models.Project.objects.filter(id=row.id).update(status=1, color=2)


        for row in join_list:
            row=row.task
            # 处理时间字符串,转换为无时区的
            expiry_date = row.expiry_date.replace(tzinfo=None)
            if now_time + timedelta(days=20) >= expiry_date and now_time + timedelta(days=20) < expiry_date:
                models.Project.objects.filter(id=row.id).update(status=2, color=3)
            elif now_time > expiry_date:
                models.Project.objects.filter(id=row.id).update(status=3, color=1)
            else:
                models.Project.objects.filter(id=row.id).update(status=1, color=2)

        # 1. 从数据库中获取两部分数据
        #     我创建的所有项目：所有药品状态
        #     我参与管理的所有项目：所有药品状态

        # 遍历过后加入到各自的地方
        projects_dict = {'临期': [], '过期': [], '正常': [], 'my': [], 'join': []}

        # 我创建的所有项目：所有药品状态
        my_project_list = models.Project.objects.filter(creator=request.People.user)

        for row in my_project_list:
            projects_dict['my'].append(row)
            if row.status == 2:
                projects_dict['临期'].append(row)
            elif row.status == 3:
                projects_dict['过期'].append(row)
            else:
                projects_dict['正常'].append(row)

        # 我参与管理的所有项目：所有药品状态
        join_projects_list = models.ProjectUser.objects.filter(participter=request.People.user)
        for row in join_projects_list:
            projects_dict['join'].append(row.task)
            if row.task.status == 2:
                projects_dict['临期'].append(row.task)  # 这个task是指整个一条的project数据
        form = ProjectForm(request)
        return render(request, 'web/project_list.html', {'form': form, 'project_dict': projects_dict})
    # POST,对话框的ajax添加项目
    form = ProjectForm(request, data=request.POST)
    if form.is_valid():
        # 为项目创建一个桶
        # "{手机号}-{时间戳}--167868"
        bucekt = "{}-{}-1325585694".format(request.People.user.mobile_phone, str(int(time()) * 1000), )
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
        # 获取持续时间
        # 从表单的清洗后数据中获取'EXP'字段的值，通常代表过期时间的天数
        EXP = form.cleaned_data['EXP']
        # 计算过期日期：当前时间加上过期时间的天数，并转换为UTC时间
        expiry_date = (warehousing_time + timedelta(days=EXP)).astimezone(timezone.utc)
        # 将带时区的时间戳转换为不带时区的时间戳
        # 这里为什么这么做：在某些情况下，可能需要移除时间的时区信息，以便在不同系统或数据库之间进行比较或存储
        form.instance.expiry_date = expiry_date.replace(tzinfo=None)
        # 创建项目
        instance = form.save()

        # 项目初始化问题类型
        issues_type_object_list = []
        for item in models.IssuesType.PROJECT_INIT_LIST:
            issues_type_object_list.append(models.IssuesType(project=instance, title=item))
        models.IssuesType.objects.bulk_create(issues_type_object_list)
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'error': form.errors})
