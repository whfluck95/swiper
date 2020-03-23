import logging

from django.utils.deprecation import MiddlewareMixin

from common import stat
from user.models import User
from libs.http import render_json

err_log = logging.getLogger('err')


class AuthorizeMiddleware(MiddlewareMixin):
    '''登陆验证中间件'''
    WHITE_LIST = [
        '/api/user/get_vcode',
        '/api/user/check_vcode',
        '/weibo/wb_auth',
        '/weibo/callback',
    ]

    def process_request(self, request):
        if request.path in self.WHITE_LIST:
            return

        uid = request.session.get('uid')
        if not uid:
            return render_json(code=stat.LoginRequired.code)
        # 获取当前用户
        request.user = User.objects.get(id=uid)


class LogicErrMiddleware(MiddlewareMixin):
    '''逻辑异常处理中间件'''
    def process_exception(slef, request, exception):
        if isinstance(exception, stat.LogicErr):
            err_log.error('LogicErr: [%s] %s' % (exception.code, exception.data))
            return render_json(data=exception.data, code=exception.code)