
from django.shortcuts import render
def project_list(request):
    """项目列表"""
    # 在中间间中把价格策略写进了request
    print(request.People.user)
    print(request.People.price_policy)

    return render(request,'web/project_list.html')