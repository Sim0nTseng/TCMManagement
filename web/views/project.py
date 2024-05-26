from datetime import datetime, timedelta

from django.http import JsonResponse
from django.shortcuts import render

from web import models
from web.forms.project import ProjectForm


def project_list(request):
    """项目列表"""
    # 在中间间中把价格策略写进了request
    if request.method == 'GET':
        # 查看项目列表
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
        # 验证通过
        form.instance.creator = request.People.user
        # 处理过期时间
        # 获取存储时间
        warehousing_time = datetime.now()
        # 获取保质期
        EXP = form.cleaned_data['EXP']
        expiry_date = warehousing_time + timedelta(days=EXP * 30)
        form.instance.expiry_date = expiry_date
        # 创建项目
        form.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})
