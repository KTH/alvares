__author__ = 'tinglev@kth.se'

import logging
from modules import environment

LOG = logging.getLogger(__name__)

FEATURE_FLAG_UTR_DELETE_ON_ZERO_REPLICAS = 'FEATURE_FLAG_UTR_DELETE_ON_ZERO_REPLICAS'

def use_feature_flag_utr_delete_on_zero_replicas():
    return use(FEATURE_FLAG_UTR_DELETE_ON_ZERO_REPLICAS)

def use(flag):
    value = environment.is_true(environment.get_env_with_default_value(flag, False))
    LOG.debug('Feature flag %s is "%s".', flag, value)
    return value
