import datetime
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt

from django.urls import reverse
from utils.encrypt import uid
from utils.pagination import Pagination
from web import models
from web.forms.issues import IssuesModelForm, IssuesReplyModelForm, InviteModelForm
from web.models import Issues


class CheckFilter(object):
    def __init__(self, name, data_list, request):
        self.name = name
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        for item in self.data_list:
            key = str(item[0])
            text = item[1]
            ck = ""
            # 判断如果当前用户请求的URL中的status和当前循环的key相等，就把checked属性加上
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:
                ck = "checked"
                value_list.remove(key)
            else:
                value_list.append(key)

            # 为自己生成URL
            # 在当前URL的基础上去增加一项
            # status=1&age=12
            query_dict = self.request.GET.copy()
            query_dict._mutable = True  # 允许修改(不然query_dict不能修改，所以要先将其变成可变的，才能修改，然后再赋值给query_dict)
            # query_dict.setlist('status', [11, 22, 33])
            # 可以得到status=11&status=22&status=33&age=12
            query_dict.setlist(self.name, value_list)
            if 'page' in query_dict:
                query_dict.pop('page')
            param_url = query_dict.urlencode()
            if param_url:
                url = "{}?{}".format(self.request.path_info,
                                     query_dict.urlencode())  # query_dict.urlencode()可以把查询字符串转换为urlencode格式
            else:
                url = self.request.path_info
            # 例如{'status':[1,2,3],'xx':[1,]}转换为status=1&status=2&status=3&xx=1
            tpl = "<a class='cell' href='{url}'><input type='checkbox' {ck}/><label>{text}</label></a>"
            html = tpl.format(url=url, ck=ck, text=text)
            yield mark_safe(html)


class SelectFilter(object):
    def __init__(self, name, data_list, request):
        self.name = name
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        yield mark_safe("<select class='select2' multiple='multiple' style='width:100%;' >")
        for item in self.data_list:
            key = str(item[0])
            text = item[1]

            selected = ""
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:
                selected = 'selected'
                value_list.remove(key)
            else:
                value_list.append(key)

            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            query_dict.setlist(self.name, value_list)
            if 'page' in query_dict:
                query_dict.pop('page')

            param_url = query_dict.urlencode()
            if param_url:
                url = "{}?{}".format(self.request.path_info, param_url)  # status=1&status=2&status=3&xx=1
            else:
                url = self.request.path_info

            html = "<option value='{url}' {selected} >{text}</option>".format(url=url, selected=selected, text=text)
            yield mark_safe(html)
        yield mark_safe("</select>")


def issues(request, nid):
    if request.method == 'GET':
        # 更具URL来做筛选
        allow_filter_name = ['issues_type', 'status', 'priority', 'assign', 'attention']
        # 筛选条件（通过用户的GET传参实现）
        # ?status=1&status=2&issues_type=1
        condition = {}
        for name in allow_filter_name:
            value_list = request.GET.getlist(name)
            if not value_list:
                continue
            condition["{}__in".format(name)] = value_list
            """
            condition{
                "status__in" = [1,2],
                "issues_type__in" = [1,]
            }
            """

        # 分页获取数据
        queryset = models.Issues.objects.filter(project_id=nid).filter(**condition)

        page_obj = Pagination(
            current_page=request.GET.get('page'),
            all_count=queryset.count(),
            base_url=request.path_info,
            query_params=request.GET,
            per_page=10,
        )
        issues_obj_list = queryset[page_obj.start:page_obj.end]
        form = IssuesModelForm(request)

        project_issues_type = models.IssuesType.objects.filter(project_id=nid).values_list('id', 'title')

        project_total_user = [(request.People.project.creator_id, request.People.project.creator.username)]
        # project_join_user = models.ProjectUser.objects.filter(task_id=nid).values_list('participter_id',
        #                                                                                'participter__username')
        # project_total_user.append(project_join_user)

        invite_form = InviteModelForm()
        context = {
            'form': form,
            'invite_form': invite_form,
            'issues_obj_list': issues_obj_list,
            'page_html': page_obj.page_html(),
            'filter_list': [
                {'title': "问题类型", 'filter': CheckFilter('issues_type', project_issues_type, request)},
                {'title': "状态", 'filter': CheckFilter('status', models.Issues.status_choices, request)},
                {'title': "优先级", 'filter': CheckFilter('priority', models.Issues.priority_choices, request)},
                {'title': "指派者", 'filter': SelectFilter('assign', project_total_user, request)},
                {'title': "关注者", 'filter': SelectFilter('attention', project_total_user, request)},
            ]
        }
        return render(request, 'web/issues.html', context)
    form = IssuesModelForm(request, data=request.POST)
    if form.is_valid():
        form.instance.project = request.People.project
        form.instance.creator = request.People.user
        form.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})


def issues_detail(request, nid, issues_id):
    """编辑问题"""
    issues_obj = models.Issues.objects.filter(id=issues_id, project_id=nid).first()
    form = IssuesModelForm(request, instance=issues_obj)
    return render(request, 'web/issues_detail.html', {'form': form, "issues_obj": issues_obj})


@csrf_exempt
def issues_record(request, nid, issues_id):
    """初始化操作记录"""
    # 判断是否品论是否可以操作
    if request.method == 'GET':
        reply_list = models.IssuesReply.objects.filter(issues_id=issues_id, issues__project=request.People.project)
        # 将queryset转换为json格式
        data_list = []
        for row in reply_list:
            data = {
                'id': row.id,
                'reply_type_text': row.get_reply_type_display(),
                'content': row.content,
                'creator': row.creator.username,
                'datetime': row.create_datetime.strftime('%Y-%m-%d %H:%M'),
                'parent_id': row.reply_id
            }
            data_list.append(data)
        return JsonResponse({'status': True, 'data': data_list})

    form = IssuesReplyModelForm(data=request.POST)
    if form.is_valid():
        form.instance.issues_id = issues_id
        form.instance.reply_type = 2
        form.instance.creator = request.People.user
        instance = form.save()
        info = {
            'id': instance.id,
            'reply_type_text': instance.get_reply_type_display(),
            'content': instance.content,
            'creator': instance.creator.username,
            'datetime': instance.create_datetime.strftime('%Y-%m-%d %H:%M'),
            'parent_id': instance.reply_id
        }

        return JsonResponse({'status': True, 'data': info})
    return JsonResponse({'status': False, 'error': form.errors})


@csrf_exempt
def issues_change(request, nid, issues_id):
    """修改问题"""
    issues_obj = models.Issues.objects.filter(id=issues_id, project_id=nid).first()
    post_dict = json.loads(request.body.decode('utf-8'))
    name = post_dict.get('name')
    value = post_dict.get('value')
    filed_obj = models.Issues._meta.get_field(name)

    def create_reply_record(content):
        new_obj = models.IssuesReply.objects.create(
            reply_type=1,
            issues=issues_obj,
            content=content,
            creator=request.People.user,
        )
        new_reply_dict = {
            'id': new_obj.id,
            'reply_type_text': new_obj.get_reply_type_display(),
            'content': new_obj.content,
            'creator': new_obj.creator.username,
            'datetime': new_obj.create_datetime.strftime('%Y-%m-%d %H:%M'),
            'parent_id': new_obj.reply_id
        }
        return new_reply_dict

    # 数据库更新
    # 1.1文本
    if name in ["subject", "desc", "start_date", "end_date", ]:
        if not value:
            if filed_obj.null:
                return JsonResponse({'status': False, 'error': '您选择的值不能为空'})
            setattr(issues_obj, name, None)
            issues_obj.save()
            msg = "{}更新为空".format(filed_obj.verbose_name)
        else:
            setattr(issues_obj, name, value)
            issues_obj.save()
            msg = "{}更新为{}".format(filed_obj.verbose_name, value)
        return JsonResponse({'status': True, 'data': create_reply_record(msg)})

    # 1.2 FK字段（指派的话要判断是否创建者或参与者）
    if name in ['issues_type', 'module', 'parent', 'assign']:
        # 用户选择为空
        if not value:
            # 不允许为空
            if not filed_obj.null:
                return JsonResponse({'status': False, 'error': "您选择的值不能为空"})
            # 允许为空
            setattr(issues_obj, name, None)
            issues_obj.save()
            change_record = "{}更新为空".format(filed_obj.verbose_name)
        else:  # 用户输入不为空
            if name == 'assign':
                # 是否是项目创建者
                if value == str(request.People.project.creator_id):
                    instance = request.People.project.creator

                else:
                    project_user_object = models.ProjectUser.objects.filter(project_id=nid,
                                                                            user_id=value).first()
                    if project_user_object:
                        instance = project_user_object.participter
                    else:
                        instance = None
                if not instance:
                    return JsonResponse({'status': False, 'error': "您选择的值不存在"})
                setattr(issues_obj, name, instance)
                issues_obj.save()
                change_record = "{}更新为{}".format(filed_obj.verbose_name, str(instance.username))  # value根据文本获取到内容
            else:
                # 条件判断：用户输入的值，是自己的值。
                instance = filed_obj.remote_field.model.objects.filter(id=value, project_id=nid).first()
                if not instance:
                    return JsonResponse({'status': False, 'error': "您选择的值不存在"})

                setattr(issues_obj, name, instance)
                issues_obj.save()
                change_record = "{}更新为{}".format(filed_obj.verbose_name, str(instance))  # value根据文本获取到内容

        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})

    # 1.3choices字段
    if name in ['priority', 'status', 'mode']:
        selected_text = None
        for key, text in filed_obj.choices:
            if str(key) == value:
                selected_text = text
            if not selected_text:
                return JsonResponse({'status': False, 'error': "您选择的值不存在"})
            setattr(issues_obj, name, value)
            issues_obj.save()
            msg = "{}更新为{}".format(filed_obj.verbose_name, selected_text)
            return JsonResponse({'status': True, 'data': create_reply_record(msg)})
    # 1.4 m2m字段
    if name == "attention":
        # {"name":"attention","value":[1,2,3]}
        if not isinstance(value, list):
            return JsonResponse({'status': False, 'error': "数据格式错误"})
        if not value:
            issues_obj.attention.set([value])
            issues_obj.save()
            msg = "{}更新为空".format(filed_obj.verbose_name)
        else:
            # values的值（关注者的用户ID） ——> id是否是项目成员（参与者、创建者）
            # 获取当前项目的所有成员
            user_dict = {str(request.People.project.creator_id): request.People.project.creator.username}
            projece_user_list = models.ProjectUser.objects.filter(project_id=nid)
            for user in projece_user_list:
                user_dict[str(user.participter_id)] = user.participter.username
            username_list = []
            for user_id in value:
                username = user_dict.get(str(user_id))
                if not username:
                    return JsonResponse({'status': False, 'error': "用户不存在，请重新设置"})
                username_list.append(username)
            issues_obj.attention.set([value])
            issues_obj.save()
            msg = "{}更新为{}".format(filed_obj.verbose_name, ",".join(username_list))
        return JsonResponse({'status': True, 'data': create_reply_record(msg)})

    return JsonResponse({'status': False, 'error': "未知错误"})


def issues_url(request, nid):
    """生成邀请码"""
    form = InviteModelForm(data=request.POST)
    if form.is_valid():
        """
        1.创建一个随机验证码
        2.验证码保存到数据库
        3.限制：只有创建者才能要求
        """
        if request.People.user != request.People.project.creator:
            form.add_error('period', '无权创建邀请码')
            return JsonResponse({'status': False, 'error': form.errors})

        random_invite_code = uid(request.People.user.mobile_phone)
        form.instance.project = request.People.project
        form.instance.code = random_invite_code
        form.instance.creator = request.People.user
        form.save()

        # 将邀请码返回给前端，前端页面展示出来
        url_path = reverse('invite_join', kwargs={'code': random_invite_code})

        url = "{scheme}://{host}{path}".format(scheme=request.scheme, host=request.get_host(), path=url_path)
        # 将验证码返回给前端，前端页面上展示出来
        return JsonResponse({'status': True, 'data': url})

    return JsonResponse({'status': False, 'error': form.errors})


def invite_join(request, code):
    """邀请码加入"""
    current_time = datetime.datetime.now()

    invite_obj = models.ProjectInvite.objects.filter(code=code).first()
    if not invite_obj:
        return render(request, 'web/invite_join.html', {'error': '邀请码不存在'})

    if invite_obj.project.creator == request.People.user:
        return render(request, 'web/invite_join.html', {'error': '创建者无需再加入项目'})

    exits = models.ProjectUser.objects.filter(task=invite_obj.project, participter=request.People.user).exists()
    if exits:
        return render(request, 'web/invite_join.html', {'error': '您已经加入过该项目'})

    # 最多允许的成员(进入这个项目的创建者的限制)
    max_transaction = models.Transaction.objects.filter(user=invite_obj.project.creator).order_by('-id').first()
    # 是否过期
    if max_transaction.pricy_policy.category == 1:
        max_member = max_transaction.pricy_policy.project_member
    else:
        if max_transaction.end_datetime < current_time:
            # 过期了，免费额度
            free_obj = models.Price.objects.filter(category=1).first()
            max_member = free_obj.project_member
        else:
            max_member = max_transaction.pricy_policy.project_member

    # 目前所有的成员/包含创建者和参与者）
    current_number = models.ProjectUser.objects.filter(task=invite_obj.project).count()
    current_member = current_number + 1
    if current_member > max_member:
        return render(request, 'web/invite_join.html', {'error': '项目人数已满，请升级套餐'})

    # 邀请码是否过期
    # Convert current_time to an aware datetime object
    # 创建时间+持续时间
    limit_datetime = invite_obj.create_datetime + datetime.timedelta(minutes=invite_obj.period)
    if current_time > limit_datetime:
        return render(request, 'web/invite_join.html', {'error': '邀请码已过期'})
    # 数量限制?
    if invite_obj.count:
        if invite_obj.use_count >= invite_obj.count:
            return render(request, 'web/invite_join.html', {'error': '邀请码已使用完'})
        invite_obj.use_count += 1
        invite_obj.save()
    # 无数量限制
    models.ProjectUser.objects.create(task=invite_obj.project, participter=request.People.user)
    invite_obj.project.join_count += 1
    invite_obj.project.save()
    return render(request, 'web/invite_join.html', {'project': invite_obj.project})
