from django.template import Library
from web import models
register = Library()

@register.inclusion_tag('inclusion/all_project_list.html')
def all_project_list(request):
    # 1.获取我创建的所有接近临期的药品
    my_project_list=models.Medicine.objects.filter(creator=request.People.user)
    # 2.获取我所管理的所有接近临期的药品
    join_project_list=models.ProjectUser.objects.filter(participter=request.People.user)

    return {'my':my_project_list,'join':join_project_list}