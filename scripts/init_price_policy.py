import base
from web import models
#防止创建很多个，写个判断
def run():
    exist=models.Price.objects.filter(category=1,title="个人免费版").exists()
    if not exist:
        models.Price.objects.create(
            category=1,
            title="个人免费版",
            price=1,
            project_num=100,
            project_member=20,
        )

if __name__ == '__main__':
    run()