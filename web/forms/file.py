from web import models

from django import forms
from web.forms.bootstrap import BootStrapForm
class FileFolderModelForm(forms.ModelForm, BootStrapForm):
    class Meta:
        model = models.File
        fields = ['name',]

    def __init__(self, request,parent_obj,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.parent_obj = parent_obj


    def clean_name(self):
        name = self.cleaned_data['name']
        # 数据库判断 当前目录下此文件夹是否已存在
        queryset = models.File.objects.filter(name=name,medicine=self.request.People.project,file_type=2)
        if self.parent_obj:
            exists=queryset.filter(parent=self.parent_obj).exists()
        else:
            exists=queryset.filter(parent__isnull=True).exists()
        if exists:
            raise forms.ValidationError('文件夹已存在')
        return name