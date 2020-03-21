from django.shortcuts import redirect
from django.core.cache import cache

from common import keys
from common import stat
from swiper import cfg
from user import logics
from user.models import User
from user.forms import UserForm, ProfileForm
from libs.http import render_json
from libs.qn_cloud import upload_to_qn


def get_vcode(request):
    '''获取短信验证码'''
    phonenum = request.GET.get('phonenum')

    # 发送验证码, 并检查是否发送成功
    if logics.send_vcode(phonenum):
        return render_json()
    else:
        return render_json(code=stat.VCODE_ERR)


def check_vcode(request):
    '''进行验证，并且登陆或注册'''
    phonenum = request.POST.get('phonenum')
    vcode = request.POST.get('vcode')

    cached_vcode = cache.get(keys.VCODE_KEY % phonenum)  # 从缓存取出验证码
    if vcode and cached_vcode and vcode == cached_vcode:
        # 取出用户
        try:
            user = User.objects.get(phonenum=phonenum)
        except User.DoesNotExist:
            # 如果用户不存在，直接创建出来
            user = User.objects.create(
                phonenum=phonenum,
                nickname=phonenum
            )
        request.session['uid'] = user.id
        return render_json(user.to_dict())
    else:
        return render_json(code=stat.INVILD_VCODE)


def wb_auth(request):
    '''用户授权页'''
    return redirect(cfg.WB_AUTH_URL)


def wb_callback(request):
    '''微博回调接口'''
    code = request.GET.get('code')
    # 获取授权令牌
    access_token, wb_uid = logics.get_access_token(code)
    if not access_token:
        return render_json(code=stat.ACCESS_TOKEN_ERR)

    # 获取用户信息
    user_info = logics.get_user_info(access_token, wb_uid)
    if not user_info:
        return render_json(code=stat.USER_INFO_ERR)

    # 执行登陆或者注册
    try:
        user = User.objects.get(phonenum=user_info['phonenum'])
    except User.DoesNotExist:
        # 如果用户不存在，直接创建出来
        user = User.objects.create(**user_info)

    request.session['uid'] = user.id
    return render_json(user.to_dict())


def get_profile(request):
    '''获取个人资料'''
    profile_data = request.user.profile.to_dict()
    return render_json(profile_data)


def set_profile(request):
    '''修改个人资料'''
    user_form = UserForm(request.POST)
    profile_form = ProfileForm(request.POST)

    # 检查 User 的数据
    if not user_form.is_valid():
        return render_json(user_form.errors, code=stat.USER_DATA_ERRR)
    # 检查 Profile 的数据
    if not profile_form.is_valid():
        return render_json(profile_form.errors, code=stat.PROFILE_DATA_ERRR)

    user = request.user
    # 保存用户的数据
    user.__dict__.update(user_form.cleaned_data)
    user.save()

    # 保存交友资料的数据
    user.profile.__dict__.update(profile_form.cleaned_data)
    user.profile.save()

    return render_json()


def upload_avatar(request):
    '''上传个人形象'''
    avatar = request.FILES.get('avatar')

    logics.handle_avatar(request.user,avatar)

    return render_json()