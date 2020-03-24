import time
import datetime

from swiper import cfg
from common import keys
from common import stat
from libs.cache import rds
from user.models import User
from social.models import Swiped, Friend


def rcmd(user):
    '''推荐可滑动的用户'''
    profile = user.profile
    today = datetime.date.today()

    # 最早出生的日期
    earliest_birthday = today - datetime.timedelta(profile.max_dating_age * 365)
    # 最晚出生的日期
    latest_birthday = today - datetime.timedelta(profile.min_dating_age * 365)

    # 取出滑过的用户的 ID
    sid_list = Swiped.objects.filter(uid=user.id).values_list('sid', flat=True)

    # 取出超级喜欢过自身，但是还没有被自己滑动过的用户的 ID
    # 使用 Redis 取出
    superliked_me_id_list = [int(uid) for uid in rds.zrange(keys.SUPERLIKED_KEY % user.id, 0, 19)]
    superliked_me_users = User.objects.filter(id__in=superliked_me_id_list)

    # 使用 ORM 取出的方式
    # who_superlike_me = Swiped.objects.filter(sid=user.id, stype='superlike')\
    #                                  .exclude(uid__in=sid_list)\
    #                                  .values_list('uid', flat=True)

    # 筛选出匹配的用户
    other_count = 20 - len(superliked_me_users)
    if other_count > 0:
        other_users = User.objects.filter(
            sex=profile.dating_sex,
            location=profile.dating_location,
            birthday__gte=earliest_birthday,
            birthday__lte=latest_birthday,
        ).exclude(id__in=sid_list)[:other_count]
        users = superliked_me_users | other_users
    else:
        users = superliked_me_users

    return users


def like_someone(user, sid):
    '''喜欢某人'''
    Swiped.swipe(user.id, sid, 'like')  # 添加滑动记录

    # 检查对方是否喜欢过自己
    if Swiped.is_liked(sid, user.id):
        # 如果对方喜欢过自己，匹配成好友
        Friend.make_friends(user.id, sid)
        # 如果对方超级喜欢过你，将对方从你的超级喜欢列表中删除
        rds.zrem(keys.SUPERLIKED_KEY % user.id, sid)
        return True
    else:
        return False


def superlike_someone(user, sid):
    '''
    超级喜欢某人

    自己超级喜欢过对方，则一定会出现在对方的推荐列表中
    '''
    Swiped.swipe(user.id, sid, 'superlike')  # 添加滑动记录

    # 将自己的 ID 写入到对方的优先推荐队列
    rds.zadd(keys.SUPERLIKED_KEY % sid, {user.id: time.time()})

    # 检查对方是否喜欢过自己
    if Swiped.is_liked(sid, user.id):
        # 如果对方喜欢过自己，匹配成好友
        Friend.make_friends(user.id, sid)
        # 如果对方超级喜欢过你，将对方从你的超级喜欢列表中删除
        rds.zrem(keys.SUPERLIKED_KEY % user.id, sid)
        return True
    else:
        return False


def dislike_someone(user, sid):
    '''不喜欢某人'''
    Swiped.swipe(user.id, sid, 'dislike')  # 添加滑动记录
    # 如果对方超级喜欢过你，将对方从你的超级喜欢列表中删除
    rds.zrem(keys.SUPERLIKED_KEY % user.id, sid)


def rewind_swiped(user):
    '''反悔一次滑动纪录'''
    # 获取今天的反悔次数
    rewind_times = rds.get(keys.REWIND_KEY % user.id, 0)

    # 检查今天反悔是否达到限制次数
    if rewind_times >= cfg.DAILY_REWIND:
        raise stat.RewindLimit

    # 找到最近一次的滑动记录
    latest_swiped = Swiped.objects.filter(uid=user.id).latest('stime')

    # 检查反悔的记录是否是五分钟之内的
    now = datetime.datetime.now()
    if (now - latest_swiped.stime).total_seconds() >= cfg.REWIND_TIMEOUT:
        raise stat.RewindTimeout

    # 检查上一次滑动是否有可能匹配成了好友
    if latest_swiped.stype in ['like', 'superlike']:
        # 删除好友关系
        Friend.break_off(user.id, latest_swiped.sid)

        # 如果上一次是超级喜欢，将自身uid从对方的优先推荐队列中删除
        if latest_swiped.stype == 'superlike':
            rds.zrem(keys.SUPERLIKED_KEY % latest_swiped.sid, user.id)

    # 还原用户的滑动积分
    score = -cfg.SWIPE_SCORE[latest_swiped.stype]
    rds.zincrby(keys.HOT_RANK_KEY, score, latest_swiped.sid)

    # 删除滑动记录
    latest_swiped.delete()

    # 更新当天的滑动次数, 同时设置过期时间到下一个凌晨
    next_zero = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)
    remain_seconds = (next_zero - now).total_seconds()
    rds.set(keys.REWIND_KEY % user.id, rewind_times + 1, int(remain_seconds))


def set_score(uid, stype):
    '''给用户设置滑动积分'''
    # 调整用户积分
    score = cfg.SWIPE_SCORE[stype]
    rds.zincrby(keys.HOT_RANK_KEY, score, uid)


def top_n(num):
    '''取出排行榜前 N 的用户信息'''
    # 从 Redis 取出排行数据
    rank_data = rds.zrevrange(keys.HOT_RANK_KEY, 0, num - 1, withscores=True)
    # 进行简单的数据清洗
    cleaned = [[int(uid), int(score)] for uid, score in rank_data]

    # 取出用户数据
    uid_list = [uid for uid, _ in cleaned]
    users = User.objects.filter(id__in=uid_list)
    users = sorted(users, key=lambda user: uid_list.index(user.id))

    # 组装返回值
    result = {}
    ignore_fields = ['phonenum', 'sex', 'birthday', 'location',
                     'vip_id', 'vip_expired']
    for idx, user in enumerate(users):
        score = cleaned[idx][1]
        u_dict = user.to_dict(*ignore_fields)
        u_dict['score'] = score
        result[idx + 1] = u_dict

    return result
