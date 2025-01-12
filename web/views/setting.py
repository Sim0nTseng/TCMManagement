from django.shortcuts import render, redirect

from utils.tecent.cos import delete_bucket
from web import models


def setting(request, nid):
    return render(request, 'web/setting.html')


def delete(request, nid):
    """删除项目"""
    if request.method == 'GET':
        return render(request, 'web/setting_delete.html')
    project_name = request.POST.get("project_name")
    if not project_name or project_name != request.People.project.name:
        return render(request, 'web/setting_delete.html', {'msg': '药品名错误，请检查该药品是否为您要删除的药品'})
    # 药名写对了，将他进行删除(只有创建者才可以删除)
    if request.People.user != request.People.project.creator:
        return render(request, 'web/setting_delete.html', {'msg': '只有项目创建者才可以删除项目'})
    try:
    # 1.删除桶
    #    - 删除桶中所有文件（找到桶中所有文件）
    #    - 删除桶中所有的碎片（找到所有的文件碎片）
    #    - 删除桶
    # 2.删除页面
    #    - 项目删除
        delete_bucket(request.People.project.bucket, request.People.project.region)
    finally:
        models.Project.objects.filter(id=nid).delete()
        return redirect('/project/list/')