__author__ = 'tinglev@kth.se'

import logging
from modules import environment

LOG = logging.getLogger(__name__)

def use_lofsdalen():
    return use('FEATURE_FLAG_LOFSDALEN')

def use(flag):
    value = environment.get_env_with_default_value(flag, False)
    LOG.info('Feature flag %s is %s.', flag, value)
    return environment.is_true(value)
