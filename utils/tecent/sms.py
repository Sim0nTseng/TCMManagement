#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.sms.v20210111 import sms_client, models
from django.conf import settings


def smsSendMessage(phone_num, template_id, template_param_list):
    try:
        # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
        # 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议采用更安全的方式来使用密钥，请参见：https://cloud.tencent.com/document/product/1278/85305
        # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
        cred = credential.Credential("AKIDyX0QQD45ABHYp5Mhy8B3pVCrPp7NvSyM", "MtZF6vhPyNuZE0kNMNlJqHcmkYElAPXU")
        # 实例化一个http选项，可选的，没有特殊需求可以跳过
        httpProfile = HttpProfile()
        # 推荐使用北极星，相关指引可访问如下链接
        # https://git.woa.com/tencentcloud-internal/tencentcloud-sdk-python#%E5%8C%97%E6%9E%81%E6%98%9F%E4%BD%BF%E7%94%A8%E7%A4%BA%E4%BE%8B
        httpProfile.endpoint = "sms.tencentcloudapi.com"

        # 实例化一个client选项，可选的，没有特殊需求可以跳过
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        # 实例化要请求产品的client对象,clientProfile是可选的
        client = sms_client.SmsClient(cred, "ap-guangzhou", clientProfile)

        # 实例化一个请求对象,每个接口都会对应一个request对象
        req = models.SendSmsRequest()
        params = {
            "PhoneNumberSet": [phone_num],
            "SmsSdkAppId": settings.TENCENT_SMS_APP_ID,
            "SignName": settings.TENCENT_SMS_SIGN,
            "TemplateId": template_id,
            "TemplateParamSet": [template_param_list]
        }
        req.from_json_string(json.dumps(params))

        # 返回的resp是一个SendSmsResponse的实例，与请求对象对应
        resp = client.SendSms(req)
        # 输出json格式的字符串回包
        resp=resp.to_json_string()
        print(resp)
        return resp

    except TencentCloudSDKException as err:
        print(err)
