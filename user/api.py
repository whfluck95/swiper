import logging

from django.shortcuts import redirect
from django.core.cache import cache

from common import keys
from common import stat
from swiper import cfg
from user import logics
from user.models import User
from user.forms import UserForm, ProfileForm
from libs.cache import rds
from libs.http import render_json

inf_log = logging.getLogger('inf')


def get_vcode(request):
    '''获取短信验证码'''
    phonenum = request.GET.get('phonenum')

    # 发送验证码, 并检查是否发送成功
    if logics.send_vcode(phonenum):
        return render_json()
    else:
        raise stat.VcodeErr


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
        inf_log.info('User(%s) login in' % user.id)
        request.session['uid'] = user.id
        return render_json(user.to_dict('vip_id', 'vip_expired'))
    else:
        raise stat.InvildVcode


def wb_auth(request):
    '''用户授权页'''
    return redirect(cfg.WB_AUTH_URL)


def wb_callback(request):
    '''微博回调接口'''
    code = request.GET.get('code')
    # 获取授权令牌
    access_token, wb_uid = logics.get_access_token(code)
    if not access_token:
        raise stat.AccessTokenErr

    # 获取用户信息
    user_info = logics.get_user_info(access_token, wb_uid)
    if not user_info:
        raise stat.UserInfoErr

    # 执行登陆或者注册
    try:
        user = User.objects.get(phonenum=user_info['phonenum'])
    except User.DoesNotExist:
        # 如果用户不存在，直接创建出来
        user = User.objects.create(**user_info)

    request.session['uid'] = user.id
    return render_json(user.to_dict('vip_id', 'vip_expired'))


def get_profile(request):
    '''获取个人资料'''
    key = keys.PROFILE_KEY % request.user.id
    profile_data = rds.get(key)
    print('先从Redis缓存获取数据: %s' % profile_data)

    if profile_data is None:
        profile_data = request.user.profile.to_dict()
        print('缓存中没有，从数据库获取: %s' % profile_data)
        rds.set(key, profile_data)
        print('将取出的数据添加到缓存')
    return render_json(profile_data)


def set_profile(request):
    '''修改个人资料'''
    user_form = UserForm(request.POST)
    profile_form = ProfileForm(request.POST)

    # 检查 User 的数据
    if not user_form.is_valid():
        raise stat.UserDataErrr(user_form.errors)
    # 检查 Profile 的数据
    if not profile_form.is_valid():
        raise stat.ProfileDataErrr(profile_form.errors)

    user = request.user
    # 保存用户的数据
    user.__dict__.update(user_form.cleaned_data)
    user.save()

    # 保存交友资料的数据
    user.profile.__dict__.update(profile_form.cleaned_data)
    user.profile.save()

    # 修改缓存
    key = keys.PROFILE_KEY % request.user.id
    rds.set(key, user.profile.to_dict())

    return render_json()


def upload_avatar(request):
    '''上传个人形象'''
    avatar = request.FILES.get('avatar')

    logics.handle_avatar.delay(request.user, avatar)

    return render_json()
