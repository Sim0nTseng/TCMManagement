from qcloud_cos import CosServiceError

from utils.tecent.cos import check_file
from web import models

from django import forms
from web.forms.bootstrap import BootStrapForm


class FileFolderModelForm(forms.ModelForm, BootStrapForm):
    class Meta:
        model = models.File
        fields = ['name', ]

    def __init__(self, request, parent_obj, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.parent_obj = parent_obj

    def clean_name(self):
        name = self.cleaned_data['name']
        # 数据库判断 当前目录下此文件夹是否已存在
        queryset = models.File.objects.filter(name=name, project=self.request.People.project, file_type=2)
        if self.parent_obj:
            exists = queryset.filter(parent=self.parent_obj).exists()
        else:
            exists = queryset.filter(parent__isnull=True).exists()
        if exists:
            raise forms.ValidationError('文件夹已存在')
        return name


class FilePostForm(forms.ModelForm):
    # etag = forms.CharField(label='ETag')

    class Meta:
        model = models.File
        exclude = ['project', 'file_type', 'update_user', 'update_datetime']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_file_path(self):
        return "https://{}".format(self.cleaned_data['file_path'])

    """
    def clean(self):
        key = self.cleaned_data['key']
        etag = self.cleaned_data['etag']
        size = self.cleaned_data['size']

        if not key or not etag:
            return self.cleaned_data

        # 向COS校验文件是否合法
        # SDK的功能
        from qcloud_cos.cos_exception import CosServiceError
        try:
            result = check_file(self.request.tracer.project.bucket, self.request.tracer.project.region, key)
        except CosServiceError as e:
            self.add_error("key", '文件不存在')
            return self.cleaned_data

        cos_etag = result.get('ETag')
        if etag != cos_etag:
            self.add_error('etag', 'ETag错误')

        cos_length = result.get('Content-Length')
        if int(cos_length) != size:
            self.add_error('size', '文件大小错误')

        return self.cleaned_data
    """
