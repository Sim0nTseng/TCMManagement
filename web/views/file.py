import json

from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from django.urls import reverse

from utils.tecent.cos import delete_files, delete_file, credential
from web import models
from web.forms.file import FileFolderModelForm, FilePostForm
from utils.encrypt import uid
from utils.tecent import cos


def File(request, nid):
    """文件列表 & 添加文件夹"""
    parent_obj = None
    folder_id = request.GET.get('folder', "")

    if folder_id.isdecimal():
        parent_obj = models.File.objects.filter(file_type=2, id=int(folder_id), project=request.People.project).first()

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
        query_set = models.File.objects.filter(project=request.People.project)
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
            'bredcrumb_list': bredcrumb_list,
            'folder_obj': parent_obj
        }
        return render(request, 'web/file.html', context)

    # post添加文件夹 & 文件记得修改
    fid = request.POST.get('fid', '')
    print(fid)
    edit_obj = None
    if fid.isdecimal():
        # 修改
        edit_obj = models.File.objects.filter(id=int(fid), file_type=2, project=request.People.project).first()
    if edit_obj:
        # 编辑
        form = FileFolderModelForm(request, parent_obj, request.POST, instance=edit_obj)
    else:
        form = FileFolderModelForm(request, parent_obj, request.POST)

    if form.is_valid():
        form.instance.project = request.People.project
        form.instance.file_type = 2
        form.instance.update_user = request.People.user
        form.instance.parent = parent_obj
        form.save()
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, "error": form.errors})


def file_delete(request, nid):
    """删除文件"""
    fid = request.GET.get('fid')
    # 删除数据库的值
    delete_obj = models.File.objects.filter(id=int(fid), project=request.People.project).first()
    if delete_obj.file_type == 1:
        # 删除文件（数据库文件删除，cos删除，项目使用空间还回去）
        # 字节
        # 删除文件时将容量还给已使用空间
        request.People.project.use_space -= delete_obj.file_size
        request.People.project.save()
        # cos删除文件
        delete_file(request.People.project.bucket, request.People.project.region, delete_obj.key)
        # 删除数据库文件
        delete_obj.delete()
        return JsonResponse({'status': True})
    else:
        # 删除文件夹（找到文件夹所有的文件）
        # 找到他下面的文件和文件夹
        total_size = 0
        folder_list = [delete_obj, ]
        key_list = []
        for folder in folder_list:
            child_list = models.File.objects.filter(project=request.People.project, parent=folder).order_by(
                '-file_type')
            for child in child_list:
                if child.file_type == 2:
                    folder_list.append(child)
                else:
                    # 文件大小
                    total_size += child.file_size
                    # 删除文件
                    key_list.append({"Key:": child.key})

        # 批量删除
        if key_list:
            delete_files(request.People.project.bucket, request.People.project.region, key_list)

        # 归还容量
        if total_size:
            request.People.project.use_space -= total_size
            request.People.project.save()

        # 删除数据库中文件
        delete_obj.delete()
        return JsonResponse({'status': True})


@csrf_exempt
def cos_credential(request, nid):
    """获取COS临时凭证"""
    file_list = json.loads(request.body.decode('utf-8'))
    # 单文件限制大小 M
    per_file_limit = request.People.price_policy.per_file_size * 1024 * 1024
    total_size_limit = request.People.price_policy.project_space * 1024 * 1024 * 1024
    total_size = 0
    for file_info in file_list:
        # 文件字节大写file_info.size、
        # 单文件限制大小 M
        if file_info['size'] > per_file_limit:
            return JsonResponse(
                {'status': False, 'error': '文件大小不能超过{}M'.format(request.People.price_policy.per_file_size)})
        total_size += file_info['size']

    # 总容量限制
    if request.People.project.use_space + total_size > total_size_limit:
        return JsonResponse({'status': False, 'error': '项目容量不足,请升级套餐'})

    data_dict = credential(request.People.project.bucket, request.People.project.region)
    return JsonResponse({'status': True, 'data': data_dict, })


@csrf_exempt
def file_post(request, nid):
    """文件上传写入到数据库"""
    """
    file_size:fileSize,
    key:key,
    parent:CURRENT_FOLDER_ID,
    Etag:data.Etag,
    file_path: data.Location,
    """
    # 数据校验，写一个Form来校验
    form = FilePostForm(request, data=request.POST)
    if form.is_valid():
        # 校验通过：写入数据库
        # form.instance.file_type=1
        # form.instance.update_user=request.People.user
        # instance=form.save() # 添加成功之后，获取到新添加的那个对象（instance.id但不可以instance.get_xx_display）
        data_dict = form.cleaned_data
        # data_dict.pop('etag')
        data_dict.update({'project': request.People.project, 'file_type': 1, 'update_user': request.People.user})
        instance = models.File.objects.create(**data_dict)

        # 项目已使用空间
        request.People.project.use_space += data_dict['file_size']
        request.People.project.save()
        result = {
            'name': instance.name,
            'file_size': instance.file_size,
            'file_type': instance.get_file_type_display(),
            'username': instance.update_user.username,
            'datetime': instance.update_datetime.strftime("%Y年%m月%d日 %H:%M"),
            'download_url': "http://localhost:8000/manage/"+str(nid)+"/cos/"+str(instance.id)+"/downlowd/"
        }
        return JsonResponse({"status":True, 'data': result})
    return JsonResponse({"status": False, 'data': "文件错误"})


def file_download(request, nid,file_id):
    """文件下载"""
    # 文件内容
    # 响应头
    # 打开文件,获取内容,去cos获取
    import requests
    file_obj=models.File.objects.filter(id=file_id, project_id=nid).first()
    res=requests.get(file_obj.file_path)
    data = res.content
    responce=HttpResponse(data)
    # 设置下载响应头
    responce['Content-Disposition']="attachment;filename="+file_obj.name
    return responce
