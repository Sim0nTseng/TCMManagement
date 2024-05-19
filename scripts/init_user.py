
import django
import os

#因为我们没有导入路径，他其实是找不到的，我们就要把TCMMangement写入sys
import sys
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
#

# 相当于编辑环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TCMManagement.settings')
#模拟django启动manage.py
django.setup() #有了就会去找os.environ['django_se....']去找

from web import models
# 往数据库添加数据：一定要连接数据库，操作，关闭连接
models.UserInfo.objects.create(username='ZhangXinyang',email='Susan@fuvk.com',password='pussypussy')