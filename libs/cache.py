import pickle

from redis import Redis as _Redis

from swiper.cfg import REDIS


class Redis(_Redis):
    def set(self, name, value, ex=None, px=None, nx=False, xx=False):
        '''Set the value at key ``name`` to ``value``

        ``ex`` sets an expire flag on key ``name`` for ``ex`` seconds.
        ``px`` sets an expire flag on key ``name`` for ``px`` milliseconds.
        ``nx`` if set to True, set the value at key ``name`` to ``value`` only
               if it does not exist.
        ``xx`` if set to True, set the value at key ``name`` to ``value`` only
               if it already exists.
        '''
        pickled_data = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
        return super().set(name, pickled_data, ex, px, nx, xx)

    def get(self, name, default=None):
        '''Return the value at key ``name``, or None if the key doesn't exist'''
        pickled_data = super().get(name)
        if pickled_data is None:
            return default
        else:
            try:
                return pickle.loads(pickled_data)
            except (TypeError, pickle.UnpicklingError):
                return pickled_data


rds = Redis(**REDIS)