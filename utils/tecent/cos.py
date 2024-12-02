from qcloud_cos import CosConfig, CosS3Client
from django.conf import settings
from qcloud_cos.cos_exception import CosServiceError, CosClientError


def creat_bucket(bucket, region):
    """
    创建桶
    :param bucket: 桶名称
    :param region: 区域
    :return:
    """
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_APP_ID, SecretKey=settings.TENCENT_COS_APP_KEY)

    client = CosS3Client(config)
    client.create_bucket(
        Bucket=bucket,
        ACL='public-read'
    )
    # 设置跨域
    cors_config = {
        'CORSRule': [
            {
                'AllowedOrigin': '*',
                'AllowedMethod': ['GET', 'PUT', 'HEAD', 'POST', 'DELETE'],
                'AllowedHeader': "*",
                'ExposeHeader': "*",
                'MaxAgeSeconds': 500
            }
        ]
    }
    client.put_bucket_cors(
        Bucket=bucket,
        CORSConfiguration=cors_config
    )


def upload_file(bucket, region, image_obj, key):
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_APP_ID, SecretKey=settings.TENCENT_COS_APP_KEY)

    client = CosS3Client(config)
    client.upload_file_from_buffer(
        Bucket=bucket,
        Body=image_obj,
        Key=key,
    )

    return "http://{}.cos.{}.mycloud.com/{}".format(bucket, region, key)


def download_file(bucket, region, key):
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_APP_ID, SecretKey=settings.TENCENT_COS_APP_KEY)
    client = CosS3Client(config)
    client.delete_object(
        Bucket=bucket,
        Key=key,
    )


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
    objects = {
        "Quiet": "true",
        "Object": key_list
    }
    client.delete_objects(
        Bucket=bucket,
        Delete=objects,
    )


def check_file(bucket, region, key):
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_APP_ID, SecretKey=settings.TENCENT_COS_APP_KEY)
    client = CosS3Client(config)
    data=client.head_bucket(
        Bucket=bucket,
        Key=key,
    )

    return data


def credential(bucket, region, ):
    """获取COS临时凭证"""
    # 生成一个临时凭证，并给前端返回
    # 1. 安装一个生成临时凭证python模块   pip install -U qcloud-python-sts
    # 2. 写代码
    from sts.sts import Sts
    config = {
        # 临时密钥有效时长，单位是秒（30分钟=1800秒）
        'duration_seconds': 1800,
        # 固定密钥 id
        'secret_id': settings.TENCENT_COS_APP_ID,
        # 固定密钥 key
        'secret_key': settings.TENCENT_COS_APP_KEY,
        # 换成你的 bucket
        'bucket': bucket,
        # 换成 bucket 所在地区
        'region': region,
        # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
        # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
        'allow_prefix': '*',
        # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
        'allow_actions': [
            'name/cos:PostObject',
            # 'name/cos:DeleteObject',
            # "name/cos:UploadPart",
            # "name/cos:UploadPartCopy",
            # "name/cos:CompleteMultipartUpload",
            # "name/cos:AbortMultipartUpload",
            "*",
        ],

    }
    sts = Sts(config)
    result_dict = sts.get_credential()
    return result_dict

def delete_bucket(bucket, region, ):
    """删除桶"""
    # 得先删除桶中所有文件和碎片
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_APP_ID, SecretKey=settings.TENCENT_COS_APP_KEY)
    client = CosS3Client(config)
    try:
        #找到桶中所有文件
        while True:
            # 每次只会获取1000个
            part_obj=client.list_objects(bucket)
            contents=part_obj.get("Contents")
            if not contents:
                # 获取不到了
                break

            # 构造特殊格式
            objects = {
                "Quiet": "true",
                "Object": [{'Key':item["Key"]} for item in contents]
            }
            client.delete_objects(
                bucket,
                objects
            )
            # 是否有截断
            if part_obj['IsTruncated'] == "false":
                break

        #找到碎片 & 删除
        while True:
            part_uploads=client.list_multipart_uploads(bucket)
            uploads=part_uploads.get("Upload")
            if not uploads:
                break
            for item in uploads:
                key=item["Key"]
                upload_id=item["UploadId"]
                client.abort_multipart_upload(
                    bucket,
                    key,
                    upload_id
                )
            if part_obj['IsTruncated'] == "false":
                break
        client.delete_bucket(bucket)
    except CosServiceError as e:
        pass