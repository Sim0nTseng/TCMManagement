from qcloud_cos import CosConfig, CosS3Client
from django.conf import settings

def creat_bucket(bucket,region):
    """
    创建桶
    :param bucket: 桶名称
    :param region: 区域
    :return:
    """
    config=CosConfig(Region=region,SecretId=settings.TENCENT_COS_APP_ID,SecretKey=settings.TENCENT_COS_APP_KEY)

    client=CosS3Client(config)
    client.create_bucket(
        Bucket=bucket,
        ACL='public-read'
    )


def upload_file(bucket,region,image_obj,key):
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_APP_ID, SecretKey=settings.TENCENT_COS_APP_KEY)

    client = CosS3Client(config)
    client.upload_file_from_buffer(
        Bucket=bucket,
        Body=image_obj,
        Key=key,
    )

    return "http://{}.cos.{}.mycloud.com/{}".format(bucket,region,key)
