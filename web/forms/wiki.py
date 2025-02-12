from web import models

from django import forms
from web.forms.bootstrap import BootStrapForm


class wikiModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.Wiki
        exclude = ['project', 'depth']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 找到想要的字段把他绑定显示的数据重置
        # 数据库中获取当前项目所有的wiki标题
        total_data_list = [("", "请选择"), ]
        data_list = models.Wiki.objects.filter(project=request.People.project).values_list('id', 'title')
        total_data_list.extend(data_list)
        self.fields['parent'].choices = total_data_list
