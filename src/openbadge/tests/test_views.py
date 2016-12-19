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
INPUT_FILE = PROJECT_DIR.format(
        "src/openbadge/tests/testdata/{}_{}_entry.txt")
HUB_NAME_PREFIX = "test_pls_delete_{}"
DATA_FILE_LOCATION = PROJECT_DIR.format("data/{}_{}.log")

def _hub_name(hub_name):
    return HUB_NAME_PREFIX.format(hub_name)

class TestDatalog(TestCase):
    

    def setUp(self):
        self.factory = RequestFactory()
        self.hubs =  [ _hub_name("one"), _hub_name("two") ]
        for hub in self.hubs:
            models.Hub.objects.create(name=hub, uuid=hub)
        # just in case there's some leftover test files
        self.delete_logs()
        
    def tearDown(self):
        self.delete_logs()

    def load_chunks(self, filename): 
        """
        Loads a given file into a json object
        """
        chunks = []
        with open(filename, "r") as loadfile:
             for line in loadfile:
                chunks.append(json.loads(line))
        return chunks

    def delete_logs(self):
        """
        For cleanup - deletes all data logs created 
        associated with testing
        """
        print "Clearing test data files"
        for f in glob.glob(DATA_FILE_LOCATION.format(HUB_NAME_PREFIX.format("*"), "*")):
            os.remove(f)

    def create_post_request(self, hub, data_type, chunks):
        """
        Create and return a post request with 
        the specifed data_type/chunks
        For sending to post_datafiles
        """
        data = { "data_type": data_type, "chunks": json.dumps(chunks) }
        request = self.factory.post(
                    '/project_key/datafiles', 
                    data,
                    HTTP_X_HUB_UUID=hub,
                    HTTP_X_APPKEY=APP_KEY)
        request.user = AnonymousUser()
        return request


    def create_and_add_data(self, hub, data_type, log_location, test_data):
        """
        Make sure that we can create files and add data to them
        """
        
        self.assertFalse(os.path.exists(log_location))
        expected_chunks = self.load_chunks(test_data)

        request = self.create_post_request(hub, data_type, expected_chunks) 
        resp = views.post_datafile(request, 'test-project')
        resp_json = json.loads(resp.content)

        self.assertTrue(os.path.exists(log_location))
        actual_chunks = self.load_chunks(log_location)
        
        self.assertEqual(len(actual_chunks), len(expected_chunks))
        self.assertEqual(resp_json["chunks_written"],
                         len(expected_chunks))
        self.assertEqual(int(resp_json["chunks_written"]), 
                         int(resp_json["chunks_received"]))
        self.assertEqual(actual_chunks, expected_chunks)
                
    def append_data(self, hub, data_type, log_location, test_data):
        """
        Make sure the we can add data to existing files
        """
        self.assertTrue(os.path.exists(log_location))
        num_existing_chunks = len(self.load_chunks(log_location))
        chunks_to_write = self.load_chunks(test_data)
        
        request = self.create_post_request(hub, data_type, chunks_to_write) 
        resp = views.post_datafile(request, 'test-project') 
        resp_json = json.loads(resp.content)
        actual_chunks = self.load_chunks(log_location)
        
        
        self.assertEqual(int(resp_json["chunks_written"]),
                         int(resp_json["chunks_received"]))
        # the number of chunks in the data file should equal the sum of
        # the number of chunks to write and the existing chunks
        self.assertEqual(len(actual_chunks), 
                         len(chunks_to_write) + num_existing_chunks)
        # the last chunk in the file should be the same as the last chunk
        # in the list of chunks to write
        self.assertEqual(actual_chunks[len(actual_chunks) - 1], 
                         chunks_to_write[len(chunks_to_write) - 1])
        
        
    def test_post_datafiles_creation(self):
        """ 
        Test file creation 
        """
        # we just want the first hub in the list
        hub_uuid = hub_name = self.hubs[0]
        self.assertTrue(models.Hub.objects.get(uuid=hub_uuid) 
                            is not None)

        # test that it works for both audio and proximity
        # with both one line and multiple
        for data_type in [ "audio", "proximity" ]:
            for entry_type in [ "single", "multi" ]:
                data_location = DATA_FILE_LOCATION.format(hub_name, data_type)
                self.create_and_add_data(
                        hub_uuid,
                        data_type, 
                        data_location, 
                        INPUT_FILE.format(entry_type, data_type)
                )
                self.delete_logs()

    def test_post_datafiles_append(self):
        # test to make sure that new incoming data is appended to the file 
        data_type = "audio"
        hub_uuid = hub_name = self.hubs[0]
        data_location = DATA_FILE_LOCATION.format(hub_name, data_type)
        self.create_and_add_data(
                    hub_uuid,
                    data_type, 
                    data_location,
                    INPUT_FILE.format("single", data_type))
        self.append_data(
                    hub_uuid,
                    data_type, 
                    data_location,
                    INPUT_FILE.format("single", data_type))

     
    def test_post_datafiles_multiple_hubs(self):
        """
        Make sure each hub gets a new file and data is added appropriately
        """
        # make sure there's no existing test logs 
        self.delete_logs()
        data_types = [ "audio", "proximity" ]
        entry_type = "single"
        data_files = []
        for hub in self.hubs:
           for data_type in data_types:
                    data_file = DATA_FILE_LOCATION.format(hub, data_type)
                    self.create_and_add_data(
                        hub,
                        data_type,
                        data_file,
                        INPUT_FILE.format(entry_type, data_type))
                    data_files.append(data_file)

        for data_file in data_files:
            self.assertTrue(os.path.exists(data_file))
