
from django import forms
from django.core.exceptions import ValidationError
from web.forms.widgets import ColorRadioSelect
from web import models
from web.forms.bootstrap import BootStrapForm

class ProjectForm(BootStrapForm,forms.ModelForm):
    # color就不会应用加form-control
    bootstrap_class_exclude = ['color']

    class Meta:
        model=models.Project
        fields=('name','priority','desc','EXP')
        widgets={
            'desc':forms.Textarea,
        }

    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request = request

    def clean_name(self):
        """项目校验"""
        name=self.cleaned_data['name']
        # 1.当前用户是否已创建过此项目(项目名是否一已存在)？

        # 1.1所有人是否已经创建过这个项目
        exits=models.Project.objects.filter(name=name,creator=self.request.People.user).exists()
        if exits:
            raise ValidationError('该任务已创建')
        # 2.当前用户是否还有额度
        # 最多创建N个药品

        # 现在已创建多少药品
        count=models.Project.objects.filter(creator=self.request.People.user).count()
        if count>= self.request.People.price_policy.project_num:
            raise ValidationError('创建任务数已上线，请购买套餐')
        return name
