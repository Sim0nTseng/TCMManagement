import collections
import datetime
import time

from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render

from web import models


def dashboard(request, nid):
    """概览"""
    # 问题数据处理
    status_dict = {}
    for key, text in models.Issues.status_choices:
        status_dict[key] = {'text': text, 'count': 0}
    # 根据status 分组统计
    isssus_data = models.Issues.objects.filter(project_id=nid).values('status').annotate(ct=Count('id'))
    # 得到<QuerySet [{'status': 2, 'ct': 3}, {'status': 5, 'ct': 1}, {'status': 1, 'ct': 1}]>
    for item in isssus_data:
        status_dict[item['status']]['count'] = item['ct']
    # 项目成员
    user_list = models.ProjectUser.objects.filter(task_id=nid).values_list('participter_id', 'participter__username')

    # 获取最近的10个问题,指派不为空的前十天动态
    top_ten = models.Issues.objects.filter(project_id=nid, assign__isnull=False).order_by('-id')[0:10]

    contex = {
        'status_dict': status_dict,
        'user_list': user_list,
        'top_ten': top_ten,
    }
    return render(request, 'web/dashboard.html', contex)


def charts(request, nid):
    """在概览页面生成highcharts图表"""
    today = datetime.datetime.now().date()
    # 最近30天，每天创建的问题数量&根据日期每天分组
    # 生成一个有序字典
    date_dict = collections.OrderedDict()
    for i in range(0, 30):
        date = today - datetime.timedelta(days=i)
        date_dict[date.strftime('%Y-%m-%d')] = [time.mktime(date.timetuple()) * 1000, 0]

    # 去数据库中查询最近30天的所有数据
    # extra(
    #         select={'ctime': "strftime('%%Y-%%m-%%d',web_issues.create_datetime)"})在新建的表中添加ctime字段，
    result = models.Issues.objects.filter(project_id=nid, create_datetime__gte=today - datetime.timedelta(30)).extra(
        select={'ctime': "DATE_FORMAT(web_issues.create_datetime, '%%Y-%%m-%%d')"}).values('ctime').annotate(
        ct=Count('id'))
    for item in result:
        date_dict[item['ctime']][1] = item['ct']
    return JsonResponse({'status': True, 'data': list(date_dict.values())})
