import collections

from django.http import JsonResponse
from django.shortcuts import render

from web import models
from django.db.models import Count


def statistics(request, nid):
    """统计页面"""
    return render(request, 'web/statistics.html')


def statistics_priority(request, nid):
    # 找到所有的问题，根据优先级分组，每个优先级的问题数量
    start = request.GET.get('start', "")
    end = request.GET.get('end', '')

    # 1.构造字典
    data_dict = collections.OrderedDict()
    for key, text in models.Issues.priority_choices:
        data_dict[key] = {"name": text, 'y': 0}
    # 2.去数据库查询所有分组得到的数据量
    result = models.Issues.objects.filter(project_id=nid, create_datetime__gte=start, create_datetime__lt=end).values(
        'priority').annotate(ct=Count('id'))
    # 3.把分组得到的数据更新到data_dict中
    for item in result:
        data_dict[item['priority']]['y'] = item['ct']
    return JsonResponse({'status': True, 'data': list(data_dict.values())})


def statistics_project_user(request, nid):
    # 获取所有的项目成员，每个人所分配的任务数量（问题类型的配比）\

    # 1.找到所有问题并且需要根据指派的用户，分组
    """
    格式
    1:{
        "name": "xxx",
        status:{
            1:0,
            2:0,
            3:0,
            4:0,
            5:0,
            6:0,
        }
    }
    """
    start = request.GET.get('start', "")
    end = request.GET.get('end', '')
    # 所有的项目成员和未指派
    all_ueser_dict = collections.OrderedDict()
    all_ueser_dict[request.People.project.creator.id] = {
        'name': request.People.project.creator.username,
        'status': {item[0]: 0 for item in models.Issues.status_choices},
    }
    all_ueser_dict[None] = {
        'name': '未指派',
        'status': {item[0]: 0 for item in models.Issues.status_choices},
    }
    user_list = models.ProjectUser.objects.filter(task_id=nid)
    for item in user_list:
        all_ueser_dict[item.participter_id] = {
            'name': item.participter.name,
            'status': {item[0]: 0 for item in models.Issues.status_choices}
        }
    # 2.去数据库获取相关的所有问题
    issues = models.Issues.objects.filter(project_id=nid, create_datetime__gte=start, create_datetime__lt=end)
    for item in issues:
        if not item.assign:
            all_ueser_dict[None]['status'][item.status] += 1
        else:
            all_ueser_dict[item.assign_id]['status'][item.status] += 1

    # 获取所有成员
    catagories = [data['name'] for data in all_ueser_dict.values()]
    # 4.构造字典
    """
    data_result_dict = {
        1:{name:新建,data:[1，2，3，4]},
        2:{name:处理中,data:[3，4，5]},
        3:{name:已解决,data:[]},
        4:{name:已忽略,data:[]},
        5:{name:待反馈,data:[]},
        6:{name:已关闭,data:[]},
        7:{name:重新打开,data:[]},
    }
    """
    data_result_dict = collections.OrderedDict()
    for item in models.Issues.status_choices:
        data_result_dict[item[0]] = {
            'name': item[1],
            'data': []
        }
    for key, text in models.Issues.status_choices:
        # key=1,text="新建"
        for row in all_ueser_dict.values():
            count = row["status"][key]
            data_result_dict[key]['data'].append(count)
    context = {
        'status': True,
        'data': {
            'category': catagories,
            'series': list(data_result_dict.values())
        }
    }
    return JsonResponse(context)