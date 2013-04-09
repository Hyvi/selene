# -*- coding: utf-8 *-*
import collections
import hashlib


class gravatar_memoized(object):

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value


@gravatar_memoized
def get_gravatar_url(email, size=48):
    md5email = hashlib.md5(email).hexdigest()
    return 'http://gravatar.com/avatar/%s?s=%s' % (md5email, size)
