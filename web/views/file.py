from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from web import models
from web.forms.file import FileFolderModelForm
from utils.encrypt import uid
from utils.tecent import cos


def File(request, nid):
    """文件列表 & 添加文件夹"""
    parent_obj = None
    folder_id = request.GET.get('folder', "")

    if folder_id.isdecimal():
        parent_obj = models.File.objects.filter(file_type=2, id=int(folder_id), medicine=request.People.project).first()

    # GET查看页面
    if request.method == 'GET':
        # 文件库的层级显示
        bredcrumb_list = []
        parent = parent_obj
        while parent:
            # bredcrumb_list.insert(0,{'id':parent.id,'name':parent.name})
            # 还可写成
            bredcrumb_list.insert(0, model_to_dict(parent, ['id', 'name']))
            parent = parent.parent

        # 当前目录下所有的文件 & 文件夹获取到即可
        query_set = models.File.objects.filter(medicine=request.People.project)
        if parent_obj:
            # 进入了某目录
            file_object_list = query_set.filter(parent=parent_obj, ).order_by('-file_type')
        else:
            # 根目录
            file_object_list = query_set.filter(parent__isnull=True).order_by('-file_type')

        form = FileFolderModelForm(request, parent_obj)

        context = {
            'form': form,
            'file_object_list': file_object_list,
            'bredcrumb_list': bredcrumb_list
        }
        return render(request, 'web/file.html', context)

    # post添加文件夹 & 文件记得修改
    fid=request.POST.get('fid','')
    print(fid)
    edit_obj=None
    if fid.isdecimal():
        # 修改
        edit_obj=models.File.objects.filter(id=int(fid),file_type=2,medicine=request.People.project).first()
    if edit_obj:
        # 编辑
        form = FileFolderModelForm(request, parent_obj, request.POST,instance=edit_obj)
    else:
        form = FileFolderModelForm(request, parent_obj, request.POST)

    if form.is_valid():
        form.instance.medicine = request.People.project
        form.instance.file_type = 2
        form.instance.update_user = request.People.user
        form.instance.parent = parent_obj
        form.save()
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, "error": form.errors})
