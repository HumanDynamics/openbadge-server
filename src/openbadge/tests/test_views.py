from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory

import json
import sys
import os
import glob

sys.path.append("..")
from openbadge import views
from openbadge import models
PROJECT_DIR = os.path.expanduser("~/openbadge-server/{}")
DATA_FILE = PROJECT_DIR.format(
        "src/openbadge/tests/testdata/{}_{}_entry.txt")

class TestDatalog(TestCase):
    
    def setUp(self):
        self.factory = RequestFactory()
        self.hub_name = "TEST_DATA_DELETE"
        self.hub_uuid = "test_hub"
        models.Hub.objects.create(name=self.hub_name, uuid=self.hub_uuid)
        # just in case cleanup didn't happen
        self.delete_logs()
        

    def load_chunks(self, filename): 
        chunks = []
        with open(filename, "r") as loadfile:
             for line in loadfile:
                chunks.append(json.loads(line)) 
        return json.dumps(chunks)

    def delete_logs(self):
        for f in glob.glob(PROJECT_DIR.format(
                    "data/{}*".format(self.hub_name))):
            print "deleting {}".format(f)
            os.remove(f)

    def create_post_request(self, data_type, chunks):
        data = { "data_type": data_type, "chunks": chunks }
        request = self.factory.post(
                    '/project_key/datalogs', 
                    data,
                    HTTP_X_HUB_UUID="test_hub",
                    HTTP_X_APPKEY=APP_KEY)
        request.user = AnonymousUser()
        return request


    def create_and_add_data(self, data_type, log_location, test_data):
        
        self.assertFalse(os.path.exists(log_location))
        expected_chunks = self.load_chunks(test_data)
        
        request = self.create_post_request(data_type, expected_chunks) 
        views.post_datalog(request, 'test-project') 

        self.assertTrue(os.path.exists(log_location))
        actual_chunks = self.load_chunks(log_location) 	
        actual_chunks_obj = json.loads(actual_chunks)
        expected_chunks_obj = json.loads(expected_chunks)

        self.assertEqual(len(actual_chunks_obj), len(expected_chunks_obj))
        # we use assert true here because otherwise it spits out a huge amount of text
        self.assertEquals(actual_chunks_obj, expected_chunks_obj)
                

        
        
    def test_post_datalogs(self):
        self.assertTrue(models.Hub.objects.get(uuid=self.hub_uuid) is not None)

        # test that it works for both audio and proximity
        # with both one line and multiple
        for data_type in [ "audio", "proximity" ]:
            for entry_type in [ "single", "multi" ]:
                log_location = PROJECT_DIR.format(
                    "data/{}_{}.log".format(self.hub_name, data_type))
                self.create_and_add_data(
                        data_type, 
                        log_location, 
                        DATA_FILE.format(entry_type, data_type)
                )
                self.delete_logs()
