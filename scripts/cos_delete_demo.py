from qcloud_cos import CosConfig, CosS3Client

from TCMManagement import settings


def delete_file(bucket, region, key):
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_APP_ID, SecretKey=settings.TENCENT_COS_APP_KEY)
    client = CosS3Client(config)
    client.delete_object(
        Bucket=bucket,
        Key=key,
    )


def delete_files(bucket, region, key_list):
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_APP_ID, SecretKey=settings.TENCENT_COS_APP_KEY)
    client = CosS3Client(config)
    objects={

    }
    client.delete_objects(
        Bucket=bucket,
        Delete=objects,
    )


if __name__ == '__main__':
    delete_files("18780047346-1731502007000-1325585694", 'ap-chengdu', ["192b3c22dc801d04f61dfec809ac5fa3.png","2832bf29f4a1fff549a6934bdf4aa52f.png"])
