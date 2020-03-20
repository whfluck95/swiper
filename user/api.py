from django.shortcuts import render

# Create your views here.

def get_vcode(request):
    """获取短信验证码"""
    phonenum = request.GET.get('phonenum')#get()不会报错


def check_vcode(request):
    """进行验证，并且登录或注册"""
    pass
