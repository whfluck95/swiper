'''程序逻辑配置和第三方平台配置'''

from urllib.parse import urlencode

# Redis 相关配置
REDIS = {
    'host': 'localhost',
    'port': 6379,
    'db': 3
}


# 滑动积分配置
SWIPE_SCORE = {
    'like': 5,
    'superlike': 7,
    'dislike': -5
}


# 反悔相关配置
DAILY_REWIND = 3  # 每日反悔次数
REWIND_TIMEOUT = 5 * 60  # 可反悔的滑动记录的秒数


# 七牛云配置
QN_ACCESS_KEY = 'kEM0sRR-meB92XU43_a6xZqhiyyTuu5yreGCbFtw'
QN_SECRET_KEY = 'QxTKqgnOb_UVldphU261qu9IdzmjkgGHh6GQVPPy'
QN_BASE_URL = 'http://py4hx1gc8.bkt.clouddn.com'
QN_BUCKET = 'sh1903'

# 云之讯配置
YZX_API = 'https://open.ucpaas.com/ol/sms/sendsms'
YZX_ARGS = {
    "sid": "e749e99071ee277991c27cf9eb62fc8d",
    "token": "bdcacd327c23b7c6a55adf2955e93c43",
    "appid": "081502fffccd4313bdf6369d36802fd0",
    "templateid": "421727",
    "param": None,
    "mobile": None,
}

# 微博配置
WB_APP_KEY = '415847342'
WB_APP_SECRET = '25bb6f5efd2f2d69177095562f031e3b'
WB_CALLBACK = 'http://127.0.0.1:8000/weibo/callback'
# 第一步: Authorize 接口
WB_AUTH_API = 'https://api.weibo.com/oauth2/authorize'
WB_AUTH_ARGS = {
    'client_id': WB_APP_KEY,
    'redirect_uri': WB_CALLBACK,
    'display': 'default'
}
WB_AUTH_URL = '%s?%s' % (WB_AUTH_API, urlencode(WB_AUTH_ARGS))
# 第二步: AccessToken 接口
WB_ACCESS_TOKEN_API = 'https://api.weibo.com/oauth2/access_token'
WB_ACCESS_TOKEN_ARGS = {
    'client_id': WB_APP_KEY,
    'client_secret': WB_APP_SECRET,
    'grant_type': 'authorization_code',
    'redirect_uri': WB_CALLBACK,
    'code': None,
}
# 第三步: 获取用户信息
WB_USER_SHOW_API = 'https://api.weibo.com/2/users/show.json'
WB_USER_SHOW_ARGS = {
    'access_token': None,
    'uid': None
}
