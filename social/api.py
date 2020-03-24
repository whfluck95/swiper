from libs.http import render_json
from social import logics
from social.models import Swiped
from social.models import Friend
from user.models import User
from vip.logics import need_permission


def get_rcmd_users(request):
    '''获取推荐用户'''
    users = logics.rcmd(request.user)
    result = [user.to_dict('vip_id', 'vip_expired') for user in users]
    return render_json(result)


def like(request):
    '''右滑-喜欢'''
    sid = int(request.POST.get('sid'))
    is_matched = logics.like_someone(request.user, sid)
    logics.set_score(sid, 'like')
    return render_json({'matched': is_matched})


@need_permission
def superlike(request):
    '''上滑-超级喜欢'''
    sid = int(request.POST.get('sid'))
    is_matched = logics.superlike_someone(request.user, sid)
    logics.set_score(sid, 'superlike')
    return render_json({'matched': is_matched})


def dislike(request):
    '''左滑-不喜欢'''
    sid = int(request.POST.get('sid'))
    logics.dislike_someone(request.user, sid)
    logics.set_score(sid, 'dislike')
    return render_json()


@need_permission
def rewind(request):
    '''
    反悔

    接口设计时的一些原则

    1. 客户端传来的任何东西不可信，所有内容都需要验证
    2. 接口的参数和返回值应保持吝啬原则，不要把与接口无关的东西传过去
    3. 服务器能够直接获取的数据，不要由客户端传递
    '''
    logics.rewind_swiped(request.user)
    return render_json()


@need_permission
def show_liked_me(request):
    '''查看谁喜欢过我'''
    user_id_list = Swiped.who_liked_me(request.user.id)
    users = User.objects.filter(id__in=user_id_list)
    result = [user.to_dict('vip_id', 'vip_expired') for user in users]
    return render_json(result)


def friend_list(request):
    '''好友列表'''
    friend_id_list = Friend.friend_ids(request.user.id)
    users = User.objects.filter(id__in=friend_id_list)
    result = [user.to_dict('vip_id', 'vip_expired') for user in users]
    return render_json(result)


def hot_rank(request):
    '''用户积分排行榜'''
    rank_data = logics.top_n(50)
    return render_json(rank_data)
