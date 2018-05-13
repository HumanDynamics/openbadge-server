from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
import simplejson as json
from django.conf import settings

import os
import glob
from datetime import datetime
from sets import Set
from itertools import groupby

from openbadge import views
from openbadge import models
APP_KEY = settings.APP_KEY
PROJECT_NAME = 'test-project'
INPUT_FILE = "openbadge-server/openbadge/tests/testdata/{}_{}_entry.txt"
HUB_NAME_PREFIX = "test_pls_delete_{}"
DATA_FILE_LOCATION = settings.DATA_DIR + "{}_{}_{}.txt"


def _hub_name(hub_name):
    # prefix all hub names with identifier
    # for easier cleanup after testing
    return HUB_NAME_PREFIX.format(hub_name)


class TestDatafile(TestCase):

    def setUp(self):

        if not os.path.exists(settings.DATA_DIR):
            os.mkdir(settings.DATA_DIR)
            # keep track of whether we created the data dir
            # and thus whether or not we should delete it at the end
            self.should_delete_data_dir = True
        else:
            self.should_delete_data_dir = False

        self.request_factory = RequestFactory()
        self.project = models.Project.objects.create(name=PROJECT_NAME)
        self.hubs = [_hub_name("one"), _hub_name("two")]
        for hub in self.hubs:
            models.Hub.objects.create(name=hub, uuid=hub, project=self.project)
        # just in case
        self.delete_logs()

    def tearDown(self):
        self.delete_logs()
        if self.should_delete_data_dir:
            os.rmdir(settings.DATA_DIR)

    def load_chunks(self, filename):
        """
        Loads a given hub data file into a json object
        """
        chunks = []
        with open(filename, "r") as loadfile:
            for line in loadfile:
                chunks.append(json.loads(line))
        return chunks

    def sort_chunks(self, chunks):
        """
        chunks are sorted by their timestamp
        """
        return sorted(chunks, key=lambda chunk: chunk["data"]["timestamp"])

    def group_chunks(self, chunks):
        """
        groups chunks by timestamp dates

        return format: { <str(date)>: <list of chunks>, ... }
        """
        grouped_chunks = {}
        for key, group in groupby(
                chunks,
                lambda chunk: datetime.fromtimestamp(chunk["data"]["timestamp"]).date().strftime('%Y-%m-%d')):
            grouped_chunks[key] = list(group)

        return grouped_chunks

    def get_dates_from_chunks(self, chunks):
        """
        returns a list of the unique set of dates that appear in
        the given chunks
        """
        dates = Set()
        for chunk in chunks:
            dates.add(datetime.fromtimestamp(chunk["data"]["timestamp"]).date().strftime('%Y-%m-%d'))

        return list(dates)

    def delete_logs(self):
        """
        For cleanup - deletes all data logs created
        associated with testing
        """
        print("Clearing test data files")
        for f in glob.glob(DATA_FILE_LOCATION.format(HUB_NAME_PREFIX.format("*"), "*", "*")):
            os.remove(f)

    def create_post_request(self, hub, data_type, chunks):
        """
        Create and return a post request with
        the specifed data_type/chunks
        For sending to post_datafiles
        """
        data = {"data_type": data_type, "chunks": json.dumps(chunks)}
        request = self.request_factory.post(
                    '/project_key/datafiles',
                    data,
                    HTTP_X_HUB_UUID=hub,
                    HTTP_X_APPKEY=APP_KEY)
        request.user = AnonymousUser()
        return request

    def create_and_add_data(self, hub_uuid, data_type, test_data):
        """
        Make sure that we can create files and add data to them

        To be called by another function that has set up the environment
        for the test
        """

        chunks_to_write = self.load_chunks(test_data)
        chunk_dates = self.get_dates_from_chunks(chunks_to_write)

        logs = {}

        for date in chunk_dates:
            log_location = DATA_FILE_LOCATION.format(hub_uuid, data_type, date)
            self.assertFalse(os.path.exists(log_location))
            logs[date] = log_location

        num_existing_files = len(os.listdir(settings.DATA_DIR))

        request = self.create_post_request(hub_uuid, data_type, chunks_to_write)
        resp = views.post_datafile(request, self.project.key)
        resp_json = json.loads(resp.content)

        self.assertEqual(int(resp_json["chunks_written"]),
                         int(resp_json["chunks_received"]))

        num_files_created = len(os.listdir(settings.DATA_DIR)) - num_existing_files
        self.assertEqual(len(chunk_dates), num_files_created)
        # since chunks are sorted before written to file,
        # we sort our expected_chunks and group them by date
        expected_chunks = self.sort_chunks(chunks_to_write)
        grouped_chunks = self.group_chunks(expected_chunks)

        self.assertEqual(len(grouped_chunks), len(logs))

        for date, log in logs.items():
            self.assertTrue(os.path.exists(log))

        actual_chunks_written = 0
        for date, expected_chunks in grouped_chunks.items():
            actual_chunks = self.load_chunks(logs[date])
            self.assertEqual(len(actual_chunks), len(expected_chunks))
            actual_chunks_written += len(actual_chunks)
            self.assertEqual(actual_chunks, expected_chunks)

        self.assertEqual(resp_json["chunks_written"],
                         actual_chunks_written)
        return logs.values()

    def append_data(self, hub_uuid, data_type, test_data):
        """
        Make sure we can add data to existing files

        To be called by another function that has set up the environment
        for the test
        """
        chunks_to_write = self.load_chunks(test_data)
        chunk_dates = self.get_dates_from_chunks(chunks_to_write)

        logs = {}
        num_existing_chunks = {}

        # gather the number of existing chunks in each log file
        # so we can be sure we wrote the correct amount to each file
        for date in chunk_dates:
            log_location = DATA_FILE_LOCATION.format(hub_uuid, data_type, date)
            self.assertTrue(os.path.exists(log_location))
            num_existing_chunks[date] = len(self.load_chunks(log_location))
            logs[date] = log_location

        request = self.create_post_request(hub_uuid, data_type, chunks_to_write)
        resp = views.post_datafile(request, self.project.key)
        resp_json = json.loads(resp.content)

        self.assertEqual(int(resp_json["chunks_written"]),
                         int(resp_json["chunks_received"]))

        sorted_chunks = self.sort_chunks(chunks_to_write)
        grouped_chunks = self.group_chunks(sorted_chunks)

        for date, expected_chunks in grouped_chunks.items():
            log_location = logs[date]
            actual_chunks = self.load_chunks(log_location)

            self.assertEqual(len(actual_chunks),
                             len(expected_chunks) + num_existing_chunks[date])

            self.assertEqual(actual_chunks[-len(expected_chunks):],
                             expected_chunks)

    def test_post_datafiles_creation(self):
        """
        Ensure files are actually created and contain appropriate data
        """
        self.delete_logs()
        # we just want the first hub in the list
        hub_uuid = self.hubs[0]
        self.assertTrue(models.Hub.objects.get(uuid=hub_uuid) is not None)

        # test that it works for both audio and proximity
        # with both one line and multiple
        for data_type in ["audio", "proximity"]:
            for entry_type in ["single", "multi"]:

                self.create_and_add_data(
                    hub_uuid,
                    data_type,
                    INPUT_FILE.format(entry_type, data_type)
                )
                self.delete_logs()

    def test_post_datafiles_append(self):
        """
        Ensures data is successfully appended to existing files without data loss
        """
        data_type = "audio"
        hub_uuid = self.hubs[0]
        self.delete_logs()
        self.create_and_add_data(
            hub_uuid,
            data_type,
            INPUT_FILE.format("spandate", data_type))
        self.append_data(
            hub_uuid,
            data_type,
            INPUT_FILE.format("spandate", data_type))

    def test_post_datafiles_multiple_hubs(self):
        """
        Make sure each hub gets a new file and data is added appropriately
        """
        # make sure there's no existing test logs
        self.delete_logs()
        data_types = ["audio", "proximity"]
        entry_type = "single"
        datafiles = []
        for hub in self.hubs:
            for data_type in data_types:
                datafiles = self.create_and_add_data(
                        hub,
                        data_type,
                        INPUT_FILE.format(entry_type, data_type))

        for datafile in datafiles:
            self.assertTrue(os.path.exists(datafile))

    def test_post_datafiles_multiple_dates(self):
        """
        Make sure data is sorted into the appropriate files
        when spanning multiple dates
        """

        self.delete_logs()
        input_file = INPUT_FILE.format("spandate", "audio")
        datafiles = self.create_and_add_data(self.hubs[0], "audio", input_file)
        for datafile in datafiles:
            self.assertTrue(os.path.exists(datafile))
