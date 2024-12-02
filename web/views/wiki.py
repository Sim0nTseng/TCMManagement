from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from web import models
from web.forms.wiki import wikiModelForm
from utils.encrypt import uid
from utils.tecent import cos

def wiki(request,nid):
    """wiki的首页"""
    wiki_id=request.GET.get('wiki_id')
    if not wiki_id or not wiki_id.isdecimal():
        return render(request,'web/wiki.html')
    wiki_obj=models.Wiki.objects.filter(id=wiki_id,medicine_id=nid).first()
    return render(request,'web/wiki.html',{'wiki_obj':wiki_obj})

def wiki_add(request,nid):
    """添加wiki"""
    if request.method == 'GET':
        form = wikiModelForm(request)
        return render(request,'web/wiki_add.html',{'form':form})
    form=wikiModelForm(request,request.POST)
    if form.is_valid():
        # 判断用户是否选择父文章
        if form.instance.parent:
            form.instance.depth=form.instance.parent.depth + 1
        else:
            form.instance.depth=1
        form.instance.medicine = request.People.project
        form.save()
        return redirect('/manage/'+str(nid)+'/wiki/')


def wiki_catalog(request,nid):
    """wiki目录"""
    # 获取当前药品的所有的
    data=models.Wiki.objects.filter(medicine=request.People.project).values('id','title','parent_id').order_by('depth','id')
    return JsonResponse({'status': True, 'data': list(data)})


def wiki_delete(request,nid):
    """
    删除文章
    :param request:
    :param nid:
    :return:
    """
    wiki_id=request.GET.get('wiki_id')
    models.Wiki.objects.filter(medicine_id=nid,id=wiki_id).delete()
    return redirect('/manage/'+str(nid)+'/wiki/')

# 免除csrftoken的认证
def wiki_edit(request,nid):
    """
    删除文章
    :param request:
    :param nid:
    :return:
    """
    wiki_id=request.GET.get('wiki_id')
    wiki_obj=models.Wiki.objects.filter(medicine_id=nid,id=wiki_id).first()
    if not wiki_obj:
        return redirect('/manage/'+str(nid)+'/wiki/')
    if request.method=='GET':
        form = wikiModelForm(request,instance=wiki_obj)
        return render(request,'web/wiki_edit.html',{'form':form})
    form = wikiModelForm(request,data=request.POST,instance=wiki_obj)
    if form.is_valid():
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1
        form.instance.medicine = request.People.project
        form.save()
        return redirect('/manage/'+str(nid)+'/wiki/')
    return render(request, 'web/wiki_edit.html')

@csrf_exempt
@xframe_options_exempt
def wiki_upload(request,nid):
    """markdown上传图片"""
    result = {
        'success': 0,
        'message': None,
        'url': None
    }
    image_obj=request.FILES.get('editormd-image-file')

    if not image_obj:
        result['message']="文件不存在"
        return JsonResponse(result)

    ext=image_obj.name.split('.')[-1]
    key="{}.{}".format(uid(request.People.user.mobile_phone),ext)
    image_url=cos.upload_file(
        request.People.project.bucket,
        request.People.project.region,
        image_obj,
        key
    )


    result['success']= 1,

    result['url']=image_url

    return JsonResponse(result)