from functools import wraps
import time
import sys
import os
import simplejson
from itertools import groupby

from datetime import datetime
from dateutil.parser import parse as parse_date
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, JsonResponse
from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from .decorators import app_view, is_god, is_own_project, require_hub_uuid
from .models import Meeting, Project, Hub, DataFile, Beacon  # Chunk  # ActionDataChunk, SamplesDataChunk

from .models import Member
from .serializers import MemberSerializer, HubSerializer, BeaconSerializer
from .permissions import AppkeyRequired, HubUuidRequired
from tablib import Dataset


TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class HttpResponseUnauthorized(HttpResponse):
    status_code = 401


def json_response(**kwargs):
    return HttpResponse(simplejson.dumps(kwargs))


def context(**extra):
    return dict(**extra)


class MemberViewSet(viewsets.ModelViewSet):
    #queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [AppkeyRequired, HubUuidRequired]
    lookup_field = 'key'

    def get_queryset(self):
        """
        Filters the members list based on the hub's project
        :return:
        """

        # hub information is validated in the permission class
        hub_uuid = self.request.META.get("HTTP_X_HUB_UUID")
        hub = Hub.objects.prefetch_related("project").get(uuid=hub_uuid)
        project = hub.project

        # Return only badges from the relevant project
        return Member.objects.filter(project=project)

    def retrieve(self, request, *args, **kwargs):
        """
        Get the badge specified by the provided key

        Also update the last time the badge was seen
        """
        badge = self.get_object()
        serializer = self.get_serializer(badge)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Creates a new member under the call hub project
        """
        hub_uuid = request.META.get("HTTP_X_HUB_UUID")
        hub = Hub.objects.prefetch_related("project").get(uuid=hub_uuid)
        project = hub.project

        # request.data is from the POST object. Adding the project id
        data = request.data.dict()
        data['project'] = project.id

        serializer = MemberSerializer(data=data)
        if serializer.is_valid():
            serializer.save()  # will call .create()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BeaconViewSet(viewsets.ModelViewSet):
    #queryset = Member.objects.all()
    serializer_class = BeaconSerializer
    permission_classes = [AppkeyRequired, HubUuidRequired]
    lookup_field = 'key'

    def get_queryset(self):
        """
        Filters the beacons list based on the hub's project
        :return:
        """

        # hub information is validated in the permission class
        hub_uuid = self.request.META.get("HTTP_X_HUB_UUID")
        hub = Hub.objects.prefetch_related("project").get(uuid=hub_uuid)
        project = hub.project

        # Return only badges from the relevant project
        return Beacon.objects.filter(project=project)

    def retrieve(self, request, *args, **kwargs):
        """
        Get the beacon specified by the provided key

        Also update the last time the beacon was seen
        """
        beacon = self.get_object()
        serializer = self.get_serializer(beacon)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Creates a new beacon under the call hub project
        """
        hub_uuid = request.META.get("HTTP_X_HUB_UUID")
        hub = Hub.objects.prefetch_related("project").get(uuid=hub_uuid)
        project = hub.project

        # request.data is from the POST object. Adding the project id
        data = request.data.dict()
        data['project'] = project.id

        serializer = BeaconSerializer(data=data)
        if serializer.is_valid():
            serializer.save()  # will call .create()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HubViewSet(viewsets.ModelViewSet):
    queryset = Hub.objects.all()
    serializer_class = HubSerializer
    permission_classes = [AppkeyRequired]
    lookup_field = 'name'


@app_view
def test(request):
    return json_response(success=True)


def test_error(request):
    raise simplejson.JSONDecodeError
    return HttpResponse()


def render_to(template):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            out = func(request, *args, **kwargs)
            if isinstance(out, dict):
                out = render(request, template, out)
            return out

        return wrapper

    return decorator


## No-Group views ######################################################################################################

###########################
# Project Level Endpoints #
###########################

@app_view
@api_view(['PUT', 'GET'])
def projects(request):
    if (request.method == 'PUT'):
        return put_project(request)
    elif (request.method == 'GET'):
        return get_project(request)
    return HttpResponseNotFound()


@is_god
@api_view(['PUT'])
def put_project(request):
    return json_response(status="Not Implemented")

@api_view(['GET'])
def get_project(request):
    hub_uuid = request.META.get("HTTP_X_HUB_UUID")
    """ng-device's id for the hub submitting this request"""

    if not hub_uuid:
        return HttpResponseBadRequest()
    try:
        hub = Hub.objects.prefetch_related("project").get(uuid=hub_uuid)
    except Hub.DoesNotExist:
        return HttpResponseNotFound()

    project = hub.project  # type: Project

    return JsonResponse(project.to_object())


###########################
# Meeting Level Endpoints #
###########################


@app_view
@api_view(['PUT', 'GET', 'POST'])
def meetings(request, project_key):
    if request.method == 'PUT':
        return put_meeting(request, project_key)
    elif request.method == 'GET':
        return get_meetings(request, project_key)
    elif request.method == 'POST':
        return post_meeting(request, project_key)
    return HttpResponseNotFound()


@api_view(['PUT'])
@is_own_project
@require_hub_uuid
def put_meeting(request, project_key):
    log_file = request.FILES.get("file")

    hub_uuid = request.META.get("HTTP_X_HUB_UUID")

    # make sure we're at the very start
    log_file.seek(0)
    # NOTE SOMETIMES THE MEETING GETS WRITTEN OUT OF ORDER
    # keep looking until we get to the meeting created line
    # this was the source (i hope) of a very frustrating bug
    meeting_meta = simplejson.loads(log_file.readline())
    while meeting_meta["type"] != "meeting started":
        meeting_meta = simplejson.loads(log_file.readline())
    log_file.seek(0)

    print meeting_meta
    meeting_data = meeting_meta['data']
    meeting_uuid = meeting_data['uuid']

    try:
        meeting = Meeting.objects.get(uuid=meeting_uuid)
        if meeting.hub.uuid != hub_uuid:
            return HttpResponseUnauthorized()

    except Meeting.DoesNotExist:
        meeting = Meeting()
        meeting.uuid = meeting_uuid
        meeting.version = meeting_data['log_version']
        meeting.project = Project.objects.get(key=project_key)

    try:
        log_file.seek(-2, 2)  # Jump to the second last byte.
        while log_file.read(1) != b"\n":  # Until EOL is found...
            log_file.seek(-2, 1)  # ...jump back the read byte plus one more.

        last = log_file.readline()  # Read last line.

        last_log = simplejson.loads(last)
        meeting.last_update_index = last_log['log_index']
        meeting.last_update_timestamp = last_log['log_timestamp']
    except IOError as e:
        print e

    log_file.seek(0)

    meeting.log_file = log_file

    meeting.hub = Hub.objects.get(uuid=hub_uuid)

    meeting.start_time = meeting_data["start_time"]

    meeting.is_complete = request.data["is_complete"] == 'true' if 'is_complete' in request.data else False

    if meeting.is_complete:
        meeting.ending_method = request.data['ending_method']
        meeting.end_time = meeting.last_update_timestamp

    meeting.save()

    return JsonResponse({'detail': 'meeting created', "meeting_key": meeting.key})


@app_view
@api_view(['GET'])
def get_meeting(request, project_key, meeting_key):
    try:
        project = Project.objects.prefetch_related("meetings").get(key=project_key)
        get_file = str(request.META.get("HTTP_X_GET_FILE")).lower() == "true"
        return JsonResponse(project.get_meeting(get_file, meeting_key))
    except Project.DoesNotExist:
        return HttpResponseNotFound()

@api_view(['GET'])
def get_meetings(request, project_key):
    try:
        project = Project.objects.prefetch_related("meetings").get(key=project_key)
        get_file = str(request.META.get("HTTP_X_GET_FILE")).lower() == "true"
        return JsonResponse(project.get_meetings(get_file))

    except Project.DoesNotExist:
        return HttpResponseNotFound()


@api_view(['POST'])
@require_hub_uuid
@is_own_project
def post_meeting(request, project_key):

    meeting = Meeting.objects.get(uuid=request.data.get('uuid'))
    chunks = request.data.get('chunks')
    meeting.is_complete = False  # Make sure we always close a meeting with a PUT.
    update_index = None
    update_time = None

    print meeting.hub.name + " appending",
    chunks = simplejson.loads(chunks)
    print chunks
    if len(chunks) == 0:
        print " NO CHUNKS",
    else:
        post_start_serial = simplejson.loads(chunks[0])['log_index']
        if post_start_serial != meeting.last_update_index + 1:
            #meeting.last_update_serial = -1
            meeting.save()
            return JsonResponse({"status": "log mismatch"})
        print "chunks",

    log = meeting.log_file.file.name
    with open(log, 'a') as f:
        for chunk in chunks:
            chunk_obj = simplejson.loads(chunk)
            update_time = chunk_obj['log_timestamp']
            update_index = chunk_obj['log_index']
            f.write(chunk)

    print "to", meeting

    if update_time and update_index:
        meeting.last_update_timestamp = update_time      # simplejson.loads(chunks[-1])['last_log_time']
        meeting.last_update_index = update_index   # simplejson.loads(chunks[-1])['last_log_serial']

    meeting.save()

    return JsonResponse({"status": "success", "meeting_key": meeting.key})

###########################
# DataFile Level Endpoints #
###########################


@is_own_project
@require_hub_uuid
@app_view
@api_view(['POST'])
def datafiles(request, project_key):
    if request.method == 'POST':
        return post_datafile(request, project_key)
    else:
        return HttpResponseNotFound()

@api_view(['POST'])
def post_datafile(request, project_key):
    """
    Accept data records posted by raspberry pi hubs

    Data will be stored in DataFiles, with each file containing
    the data of a single type (proximity | audio), for a single hub,
    on a single day.

    Data may be posted from any date, but must end up in the appropriate
    file for the date it originated on

    A "chunk" is a single data entry (as a json object) collected from the badges
    We consider these a unit of data, representing:
     - approx. five seconds of vocal activity data
     - a proximity ping
    Depending on the type of the incoming data.
    """
    # this will probably be slow for very large inputs
    # however the maximum size a file that is pending upload on the hub
    # can be is currently 15MB. This works out to ~26k entries.
    # (approx 35 hours of total audio data)
    # its unlikely for any hub to go very long without uploading
    # not too worried about it right now

    # using this header for consistency with meeting api
    hub_uuid = request.META.get("HTTP_X_HUB_UUID")
    hub = Hub.objects.get(uuid=hub_uuid)

    if not request.data.get("chunks"):
        return JsonResponse({
            "status": "failed",
            "details": "No data provided!",
            "chunks_written": 0,
            "chunks_received": 0
        }, status_code=400)

    chunks = request.data.get("chunks")

    # sometimes we don't get json objects from the request object
    # (with tests, but I don't know if it happens anywhere else?)
    # we need it in json instead of a list of strings so we can sort/operate on it
    if not isinstance(chunks, dict) and not isinstance(chunks, list):
        chunks = simplejson.loads(chunks)

    # we sort the incoming data to be able to properly group the data
    chunks = sorted(chunks, key=lambda chunk: chunk["data"]["timestamp"])

    # now group by date for bulk writing to appropriate file
    grouped_chunks = {}
    for key, group in groupby(
            chunks,
            lambda chunk: datetime.fromtimestamp(chunk["data"]["timestamp"]).date().strftime('%Y-%m-%d')):
        grouped_chunks[key] = list(group)
    # grouped_chunks is now in the format { <date>: [ <chunk1>, <chunk2>, ...], ... }

    data_type = request.data.get("data_type")

    # not sure if nested or separate helper func is better
    # its more convenient to have it here (don't need to pass params)
    # but its ~slightly~ faster to have it outside
    # potentially dont need this at all, just wanted to clean the loop up a bit
    def get_or_create_datafile(datafile_uuid, date):
        datafile, _ = DataFile.objects.get_or_create(
            uuid=datafile_uuid,
            defaults={
                'data_type': data_type,
                'hub': hub,
                'date': date,
                'project': Project.objects.get(key=project_key),
            })

        return datafile

    # we keep track of chunks written and received as a
    # very basic way to ensure data integrity
    chunks_received = len(chunks)
    chunks_written = 0

    # we're now ready to write the data to file
    for date, chunks_to_write in grouped_chunks.items():
        datafile_uuid = hub.uuid + "_" + data_type + "_" + date
        # we want the last chunk for record keeping & data consistency
        last_chunk = chunks_to_write[-1]["data"]["timestamp"]
        datafile = get_or_create_datafile(datafile_uuid, date)
        with open(datafile.filepath, 'a') as f:
            try:
                f.writelines(simplejson.dumps(chunk) + "\n" for chunk in chunks_to_write)
                chunks_written += len(chunks_to_write)
                datafile.last_chunk = last_chunk
                datafile.save()
            except IOError as e:
                # if we fail, stop trying and tell somebody
                # TODO we need logging
                print("Uh oh! Write error : " + str(e))
                return JsonResponse({
                        "status": "failed",
                        "chunks_written": chunks_written,
                        "chunks_received": chunks_received
                    },
                    status_code=500)

    return JsonResponse({
        "status": "success",
        "chunks_written": chunks_written,
        "chunks_received": chunks_received
    })


#######################
# Hub Level Endpoints #
#######################

@app_view
@api_view(['PUT', 'GET', 'POST'])
def hubs(request, project_key):
    if request.method == 'PUT':
        return put_hubs(request, project_key)
    elif request.method == 'GET':
        return get_hubs(request, project_key)
    elif request.method == 'POST':
        return post_hubs(request, project_key)
    return HttpResponseNotFound()


@api_view(['PUT'])
def put_hubs(request, project_key):
    hub_uuid = request.META.get("HTTP_X_HUB_UUID")
    if hub_uuid:
        hub = Hub()
        hub.uuid = hub_uuid
        hub.project = Project.objects.get(name="OB-DEFAULT")
        hub.name = "New Hub"
        hub.save()
        return HttpResponse()

    return HttpResponseBadRequest()


@is_own_project
@require_hub_uuid
@api_view(['GET'])
def get_hubs(request, project_key):
    hub_uuid = request.META.get("HTTP_X_HUB_UUID")
    last_update = request.META.get("HTTP_X_LAST_MEMBER_UPDATE")
    if not hub_uuid:
        return HttpResponseBadRequest()
    try:
        hub = Hub.objects.get(uuid=hub_uuid)
    except Hub.DoesNotExist:
        return HttpResponseNotFound()
    if not last_update:
        return JsonResponse(hub.get_object(0))
    return JsonResponse(hub.get_object(float(last_update)-10)) # account for some amount of async behaviour


@is_own_project
@require_hub_uuid
@is_god
@api_view(['POST'])
def post_hubs(request, project_key):
    return JsonResponse({"status": "Not Implemented"})


#########################
# Badge Level Endpoints #
#########################

@is_own_project
@require_hub_uuid
@app_view
@api_view(['PUT', 'GET', 'POST'])
def members(request, project_key):
    if request.method == 'PUT':
        return put_members(request, project_key)
    elif request.method == 'GET':
        return get_members(request, project_key)
    elif request.method == 'POST':
        return post_members(request, project_key)
    return HttpResponseNotFound()


@is_god
@api_view(['PUT'])
def put_members(request, project_key):
    return JsonResponse({"status": "Not Implemented"})



@is_god
@api_view(['GET'])
def get_members(request, project_key):
    return JsonResponse({"status": "Not Implemented"})


@api_view(['POST'])
def post_members(request, project_key):

    return JsonResponse({"status": "Not Implemented"})


#########################
# Beacon Level Endpoints #
#########################

@is_own_project
@require_hub_uuid
@app_view
@api_view(['PUT', 'GET', 'POST'])
def beacons(request, project_key):
    if request.method == 'PUT':
        return put_beacons(request, project_key)
    elif request.method == 'GET':
        return get_beacons(request, project_key)
    elif request.method == 'POST':
        return post_beacons(request, project_key)
    return HttpResponseNotFound()


@is_god
@api_view(['PUT'])
def put_beacons(request, project_key):
    return JsonResponse({"status": "Not Implemented"})


@is_god
@api_view(['GET'])
def get_beacons(request, project_key):
    return JsonResponse({"status": "Not Implemented"})


@api_view(['POST'])
def post_beacons(request, project_key):

    return JsonResponse({"status": "Not Implemented"})


#########################
# Test #
#########################
@api_view(['GET'])
def showip(request):
    remote_addr = request.META.get("REMOTE_ADDR")
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded is not None:
        return JsonResponse({"HTTP_X_FORWARDED_FOR": x_forwarded})
    else:
        return JsonResponse({"REMOTE_ADDR":remote_addr})
