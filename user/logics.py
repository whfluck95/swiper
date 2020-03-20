"""逻辑处理封装 便于复用"""
import requests
import random
from swiper import cfg



def gen_randcode(length):
    """产生指定长度的随机码"""
    chars = [str(random.randint(0,9) for i in range(length))]
    return ''.join(chars)

def send_vcode(phone):
    """发送验证"""
    vcode = gen_randcode(6)
    print(('验证码',vcode))

    sms_args = cfg.YZX_ARGS.copy()
    sms_args['mobile'] = phone
    sms_args['param'] = vcode
    response = requests.post(cfg.YZX_API,json=sms_args)
    return response
