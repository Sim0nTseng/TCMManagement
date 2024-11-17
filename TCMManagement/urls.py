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

from web.views import account, home, project, manage, wiki,file

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', account.register),
    path('send/sms/', account.send_sms),
    path('login/sms/', account.login_sms),
    path('login/', account.login),
    path('images/code/', account.image_code),
    path('index/', home.index),
    path('logout/', home.logout),

    # 项目管理
    path('project/list/', project.project_list),

    # 项目管理
    path('manage/<int:nid>/dashboard/', manage.manage_dashboard),
    path('manage/<int:nid>/issue/', manage.manage_issue),

    # wiki
    path('manage/<int:nid>/wiki/', wiki.wiki),
    path('manage/<int:nid>/wiki/add/', wiki.wiki_add),
    path('manage/<int:nid>/wiki/catalog/', wiki.wiki_catalog),
    path('manage/<int:nid>/wiki/delete/', wiki.wiki_delete),
    path('manage/<int:nid>/wiki/edit/', wiki.wiki_edit),
    path('manage/<int:nid>/wiki/upload/', wiki.wiki_upload),

    # File
    path('manage/<int:nid>/file/', file.File),
]
