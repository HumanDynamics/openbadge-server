import simplejson, datetime
from decimal import Decimal

from django.test import TestCase, Client
from django.conf import settings

from django.db import transaction

from rest_framework_expiring_authtoken.models import ExpiringToken

class APITest(TestCase):

    def setUp(self):
        pass

