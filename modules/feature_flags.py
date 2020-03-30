__author__ = 'tinglev@kth.se'

from modules import environment

def use_lofsdalen():
    return use('FEATURE_FLAG_LOFSDALEN')

def use(flag):
    value = environment.get_env_with_default_value(flag, False)
    return environment.is_true(value)
