import os
import random
import logging

import requests
from django.core.cache import cache

from swiper import cfg
from common import keys
from libs.qn_cloud import upload_to_qn
from tasks import celery_app

inf_log = logging.getLogger('inf')


def gen_randcode(length: int) -> str:
    '''产生出指定长度的随机码'''
    chars = [str(random.randint(0, 9)) for i in range(length)]
    return ''.join(chars)


def send_vcode(phone):
    vcode = gen_randcode(6)
    cache.set(keys.VCODE_KEY % phone, vcode, 180)  # 将验证码保存到缓存中, 并设置过期时间
    inf_log.info('验证码: %s' % vcode)

    sms_args = cfg.YZX_ARGS.copy()
    sms_args['mobile'] = phone
    sms_args['param'] = vcode
    response = requests.post(cfg.YZX_API, json=sms_args)

    # 检查最终返回值
    if response.status_code == 200:
        result = response.json()
        if result['code'] == '000000':
            return True
    return False


def get_access_token(code):
    '''获取微博的授权令牌'''
    args = cfg.WB_ACCESS_TOKEN_ARGS.copy()
    args['code'] = code
    response = requests.post(cfg.WB_ACCESS_TOKEN_API, data=args)
    # 检查返回值
    if response.status_code == 200:
        result = response.json()
        access_token = result['access_token']
        wb_uid = result['uid']
        return access_token, wb_uid
    return None, None


def get_user_info(access_token, wb_uid):
    args = cfg.WB_USER_SHOW_ARGS.copy()
    args['access_token'] = access_token
    args['uid'] = wb_uid
    response = requests.get(cfg.WB_USER_SHOW_API, params=args)
    # 检查返回值
    if response.status_code == 200:
        result = response.json()
        user_info = {
            'phonenum': 'WB_%s' % wb_uid,
            'nickname': result['screen_name'],
            'sex': 'female' if result['gender'] == 'f' else 'male',
            'avatar': result['avatar_hd'],
            'location': result['location'].split(' ')[0],
        }
        return user_info
    return None


def save_upload_avatar(user, upload_avatar):
    '''保存上传的头像'''
    filename = 'Avatar-%s' % user.id  # 文件名
    filepath = '/tmp/%s' % filename   # 文件路径

    with open(filepath, 'wb') as fp:
        for chunk in upload_avatar.chunks():
            fp.write(chunk)

    return filename, filepath


@celery_app.task
def handle_avatar(user, upload_avatar):
    '''处理个人头像'''
    # 将文件保存到本地
    filename, filepath = save_upload_avatar(user, upload_avatar)

    # 将文件上传到七牛
    avatar_url = upload_to_qn(filename, filepath)

    # 保存 avatar_url
    user.avatar = avatar_url
    user.save()

    # 删除本地临时文件
    os.remove(filepath)
