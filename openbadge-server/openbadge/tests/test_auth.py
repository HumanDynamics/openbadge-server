from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
import simplejson as json
from django.conf import settings

import os
import glob

from openbadge import views
from openbadge import models
APP_KEY = settings.APP_KEY
PROJECT_DIR = os.path.expanduser("~/openbadge-server/{}")

"""
URLS is a list of tuples of endpoints and whether they require a hub uuid
URLS = [ 
    "/hubs", 
    "/badges", 
    "/badges/test", 
    "/project"
"""

class TestPermissions(TestCase)

    def setUp(self):
        self.factory = RequestFactory()
        self.hubs =  [ _hub_name("one"), _hub_name("two") ]
        for hub in self.hubs:
            models.Hub.objects.create(name=hub, uuid=hub)
        models.Member.objects.create(name="test", uuid="test", key="test")
        

