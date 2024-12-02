"""
URL configuration for TCMManagement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from web.views import account, home, project, manage, wiki, file, setting, issues, dashboard, statistics

urlpatterns = [

    path('admin/', admin.site.urls),
    path('register/', account.register),
    path('send/sms/', account.send_sms),
    path('login/sms/', account.login_sms),
    path('login/', account.login),
    path('images/code/', account.image_code),
    path('index/', home.index),
    path('logout/', home.logout),

    # 价格
    path('price/', home.price, name='price'),
    path('payment/<int:policy_id>/', home.payment, name='payment'),
    path('pay/', home.pay, name='pay'),
    path('pay/', home.pay_notify, name='pay_notify'),

    # 项目管理
    path('project/list/', project.project_list),

    # 统计页面
    path('manage/<int:nid>/statistics/', statistics.statistics),
    path('manage/<int:nid>/statistics/priority/', statistics.statistics_priority),
    path('manage/<int:nid>/statistics/project_user/', statistics.statistics_project_user),
    # 项目管理(概览)
    path('manage/<int:nid>/dashboard/', dashboard.dashboard),

    path('manage/<int:nid>/dashboard/charts/', dashboard.charts),

    # wiki
    path('manage/<int:nid>/wiki/', wiki.wiki),
    path('manage/<int:nid>/wiki/add/', wiki.wiki_add),
    path('manage/<int:nid>/wiki/catalog/', wiki.wiki_catalog),
    path('manage/<int:nid>/wiki/delete/', wiki.wiki_delete),
    path('manage/<int:nid>/wiki/edit/', wiki.wiki_edit),
    path('manage/<int:nid>/wiki/upload/', wiki.wiki_upload),

    # File
    path('manage/<int:nid>/file/', file.File),
    path('manage/<int:nid>/file/delete/', file.file_delete),
    path('manage/<int:nid>/file/post/', file.file_post),

    # COS
    path('manage/<int:nid>/cos/cos_credential/', file.cos_credential),
    path('manage/<int:nid>/cos/<int:file_id>/downlowd/', file.file_download),

    # 配置
    path('manage/<int:nid>/setting/', setting.setting),
    path('manage/<int:nid>/delete/', setting.delete),

    # 问题
    path('manage/<int:nid>/issues/', issues.issues),
    path('manage/<int:nid>/issues/detail/<int:issues_id>/', issues.issues_detail),
    path('manage/<int:nid>/issues/record/<int:issues_id>/', issues.issues_record),
    path('manage/<int:nid>/issues/change/<int:issues_id>/', issues.issues_change),
    path('manage/<int:nid>/issues/invite/', issues.issues_url),
    # url(r'^invite/join/(?P<code>\w+)/$', issues.invite_join, name='invite_join'),
    path('invite/join/<str:code>/', issues.invite_join, name='invite_join')
]
