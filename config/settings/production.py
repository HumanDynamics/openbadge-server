# -*- coding: utf-8 -*-
"""
Production settings

"""

import socket
import os
from .common import *  # noqa

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool('DJANGO_DEBUG', default=False)




# CACHING
# ------------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': ''
    }
}

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = '/www/static'

DATA_DIR="/data/"
MEETINGS_DIR="data"


