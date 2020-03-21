from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

from common import stat
from user.models import User

class AuthorizeMiddleware(MiddlewareMixin):
    """登录验证中间件"""
    def process_request(self,request):
        uid = request.session.get('uid')
        if not uid:
            return JsonResponse({'code':stat.LOGIN_REQUIRED,'data':None})
        #获取当前用户
        request.user = User.objects.get(id=uid)