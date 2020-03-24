from datetime import date, datetime

from django.db import models
from django.db.models import query

from libs.cache import rds
from common.keys import MODEL_KEY


def get(self, *args, **kwargs):
    '''带缓存处理的 objects.get() 方法'''
    # 从缓存获取数据
    pk = kwargs.get('pk') or kwargs.get('id')
    if pk is not None:
        key = MODEL_KEY % (self.model.__name__, pk)
        model_obj = rds.get(key)
        if isinstance(model_obj, self.model):
            return model_obj

    # 缓存中没有，从数据库获取
    model_obj = self._get(*args, **kwargs)

    # 将取出的数据写入缓存
    key = MODEL_KEY % (self.model.__name__, model_obj.pk)
    rds.set(key, model_obj)

    return model_obj


def save(self, force_insert=False, force_update=False, using=None,
         update_fields=None):
    # 使用原 save() 函数将数据写入数据库
    self._save(force_insert, force_update, using, update_fields)

    # 将 model_obj 保存到缓存
    key = MODEL_KEY % (self.__class__.__name__, self.pk)
    rds.set(key, self)


def to_dict(self, *ignore_fields):
    '''将 model_obj 封装成一个字典'''
    attr_dict = {}
    for field in self.__class__._meta.fields:
        key = field.attname
        if key in ignore_fields:
            continue

        value = getattr(self, key)

        if isinstance(value, (date, datetime)):
            value = str(value)

        attr_dict[key] = value
    return attr_dict


def patch_orm():
    '''通过 Monkey Patch 的方式给原 ORM 增加缓存处理'''
    # 替换 get 方法
    query.QuerySet._get = query.QuerySet.get
    query.QuerySet.get = get

    # 替换 save 方法
    models.Model._save = models.Model.save
    models.Model.save = save

    models.Model.to_dict = to_dict