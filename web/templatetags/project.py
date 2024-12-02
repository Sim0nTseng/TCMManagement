from django.template import Library
from web import models
register = Library()

@register.inclusion_tag('inclusion/all_project_list.html')
def all_project_list(request):
    # 1.获取我创建的所有接近临期的药品
    my_project_list=models.Medicine.objects.filter(creator=request.People.user)
    # 2.获取我所管理的所有接近临期的药品
    join_project_list=models.ProjectUser.objects.filter(participter=request.People.user)

    return {'my':my_project_list,'join':join_project_list,'request':request}


@register.inclusion_tag('inclusion/manage_menu_list.html')
def manage_menu_list(request):
    """
    生成管理菜单列表

    参数:
        request (HttpRequest): Django 请求对象

    返回:
        dict: 包含菜单数据的字典

    用法:
        在模板中使用 `{% manage_menu_list request %}` 调用此函数
    """
    # 定义一个列表，包含多个字典，每个字典表示一个菜单选项
    data_list = [
        {
            'title': '概览',
            'url': '/manage/' + str(request.People.project.id) + '/dashboard/',
            'class': ''
        },
        {
            'title': '交流',
            'url': '/manage/' + str(request.People.project.id) + '/wiki/',
            'class':''
        },
        {
            'title': '统计',
            'url': '/manage/' + str(request.People.project.id) + '/statistics/',
            'class': ''
        },
        {
            'title': '问题',
            'url': '/manage/' + str(request.People.project.id) + '/issues/',
            'class': ''
        },
        {
            'title': '文件',
            'url': '/manage/' + str(request.People.project.id) + '/file/',
            'class': ''
        },
        {
            'title': '配置',
            'url': '/manage/' + str(request.People.project.id) + '/setting/',
            'class': ''
        }
    ]

    # 遍历菜单数据列表
    for item in data_list:
        # 如果当前请求的路径以某个菜单选项的 URL 开头，则将该菜单选项标记为激活状态
        if request.path_info.startswith(item['url']):
            item['class'] = 'active'

    # 返回包含菜单数据的字典
    return {'data_list': data_list}
