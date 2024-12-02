#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django import forms
from web.forms.bootstrap import BootStrapForm
from web import models


class IssuesModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.Issues
        exclude = ['project', 'creator', 'create_datetime', 'latest_update_datetime']
        widgets = {
            "assign": forms.Select(attrs={'class': "selectpicker", "data-live-search": "true"}),
            "attention": forms.SelectMultiple(
                attrs={'class': "selectpicker", "data-live-search": "true", "data-actions-box": "true"}),
            "parent": forms.Select(attrs={'class': "selectpicker", "data-live-search": "true"}),
            "start_date": forms.DateTimeInput(attrs={'autocomplete': "off"}),
            "end_date": forms.DateTimeInput(attrs={'autocomplete': "off"})
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 数据初始化问题
        # 获取当前项目的所有问题类型values_list数组（1," "）
        self.fields["issues_type"].choices = models.IssuesType.objects.filter(
            project=request.People.project).values_list("id", "title")

        # 获取当前项目的所有模块
        module_list = [("", "没有选择任何项")]
        module_object_list = models.Module.objects.filter(project=request.People.project).values_list("id", "title")
        module_list.extend(module_object_list)
        self.fields["module"].choices = module_list

        # 指派和关注者
        # 数据库找到当前项目的参与者和创建者
        # 先找创建者
        totol_user_list = [(request.People.project.creator_id, request.People.project.creator.username), ]
        # 再找参与者
        project_user_object_list = models.ProjectUser.objects.filter(task=request.People.project).values_list("id",
                                                                                                             "participter__username")
        totol_user_list.extend(project_user_object_list)


        # 给指派和关注者字段添加数据
        self.fields["assign"].choices = [("","没有选中任何项")]+totol_user_list
        self.fields["attention"].choices = totol_user_list

        #4.当前项目已创建的问题
        parent_list=[("","没有选择任何项")]
        parent_obj_list=models.Issues.objects.filter(project=request.People.project).values_list("id","subject")
        parent_list.extend(parent_obj_list)
        self.fields["parent"].choices = parent_list

class IssuesReplyModelForm(forms.ModelForm):
    class Meta:
        model = models.IssuesReply
        fields = ['content', 'reply']


class InviteModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.ProjectInvite
        fields = ['period', 'count']