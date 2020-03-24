from django.db import models


class Vip(models.Model):
    '''会员表'''
    name = models.CharField(max_length=10, unique=True, verbose_name='会员名称')
    level = models.IntegerField(default=0, verbose_name='会员等级')
    price = models.FloatField(default=0.0, verbose_name='当前会员对应的价格')
    days = models.IntegerField(default=0, verbose_name='购买的天数')

    def has_perm(self, perm_name):
        '''检查当前VIP是否具有某个权限'''
        perm = Permission.objects.filter(name=perm_name).only('id').first()
        return VipPermRelation.objects.filter(vip_id=self.id, perm_id=perm.id)\
                                      .exists()


class Permission(models.Model):
    '''权限表'''
    name = models.CharField(max_length=20, unique=True, verbose_name='权限名称')
    desc = models.TextField(verbose_name='权限的描述')


class VipPermRelation(models.Model):
    '''
    会员和权限的关系表

    关系：
        一级会员  超级喜欢
        二级会员  超级喜欢
        二级会员  反悔3次
        三级会员  超级喜欢
        三级会员  反悔3次
        三级会员  查看喜欢过我的人
    '''
    vip_id = models.IntegerField(verbose_name='会员的ID')
    perm_id = models.IntegerField(verbose_name='权限的ID')
