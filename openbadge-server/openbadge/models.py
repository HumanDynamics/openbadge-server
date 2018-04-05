# coding=utf-8
import datetime
import os
import pytz
import random
import json as simplejson
import string
import time
import uuid


from decimal import Decimal

from django.utils import timezone
from django.conf import settings
from django.contrib.auth import models as auth_models
from django.core.files.storage import FileSystemStorage
from django.db import models
from jsonfield import JSONField
from math import floor
from django.core.validators import MaxValueValidator, MinValueValidator


def key_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class BaseModel(models.Model):
    """
    Base model from which all other models should inherit. It has a unique key and other nice fields, like a unique id.
    If you override this class, you should probably add more unique identifiers, like a uuid or hash or something.
    """
    id = models.AutoField(primary_key = True)
    key = models.CharField(max_length=10, unique=True, db_index=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)  

    def generate_key(self, length=10):
        if not self.key:
            for _ in range(10):
                key = key_generator(length)
                if not type(self).objects.filter(key=key).count():
                    self.key = key
                    break

    def save(self, *args, **kwargs):
        self.generate_key()
        super(BaseModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class BaseModelMinimal(models.Model):
    """
    Base model from which all other models should inherit. It has a unique key and other nice fields, like a unique id.
    If you override this class, you should probably add more unique identifiers, like a uuid or hash or something.
    """
    key = models.CharField(max_length=10, unique=True, db_index=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)  

    def generate_key(self, length=10):
        if not self.key:
            for _ in range(10):
                key = key_generator(length)
                if not type(self).objects.filter(key=key).count():
                    self.key = key
                    break

    def save(self, *args, **kwargs):
        self.generate_key()
        super(BaseModelMinimal, self).save(*args, **kwargs)

    class Meta:
        abstract = True




class UserBackend(object):
    def authenticate(self, email=None, uuid=None):
        try:
            user = OpenBadgeUser.objects.get(email=email)

            if user.email != email:
                return None

        except OpenBadgeUser.DoesNotExist:
            user = OpenBadgeUser(email=email, phone_uuid=uuid, username=email)
            user.save()
        except OpenBadgeUser.MultipleObjectsReturned:
            return None

        return user

    def get_user(self, user_id):
        try:
            return OpenBadgeUser.objects.get(pk=user_id)
        except OpenBadgeUser.DoesNotExist:
            return None


def fix_email(cls):
    field = cls._meta.get_field('email')
    field.required = True
    field.blank = False
    field._unique = True
    field.db_index = True

    return cls

def upload_to(self, filename):
    location =  "/".join((
        settings.DATA_DIR.strip("/"),
        str(self.project.key),
        self.project.key + "_" + self.uuid + os.path.splitext(filename)[1]))
    return location


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name):
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


##########################################################################################
def _now_as_epoch():
    return round(Decimal(time.time()), 0) 

@fix_email
class OpenBadgeUser(auth_models.AbstractUser, BaseModel):
    pass


def _to_timestamp(dt):
    return (dt - datetime.datetime(1970, 1, 1).replace(tzinfo=pytz.UTC)).total_seconds()

class Project(BaseModel):
    """
    Definition of the Project, which is an `organization`-level collection of hubs, badges, and meetings
    """

    name = models.CharField(max_length=64)
    """Human readable identifier for this project (Apple, Google, etc.)"""
    #id = models.AutoField(primary_key = True)
    advertisment_project_id = models.IntegerField(unique=True, default=1,validators=[MaxValueValidator(254), MinValueValidator(1)])

    def __unicode__(self):
        return unicode(self.name)


    def get_meetings(self, file):
        return {
            'meetings': {
                meeting.key: meeting.to_object(file) for meeting in self.meetings.all()
            }
        }

    def get_meeting(self, file, meeting_uuid):
        meeting = self.meetings.get(uuid=meeting_uuid)
        return { meeting.key: meeting.to_object(file) }

    def to_object(self):
        """for use in HTTP responses, gets the id, name, members, and a map form badge_ids to member names"""
        return {
            'project_id': self.advertisment_project_id,
            'key': self.key,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
            'name': self.name,
            'badge_map': {
                member.badge: {
                    "name": member.name,
                    "key": member.key,
                    "id": member.id,
                    "observed_id": member.observed_id,
                    "active": member.active
                } for member in self.members.all()
            },
            'members': {
                member.name: member.to_dict() for member in self.members.all()
            },

            'beacon_map': {
                beacon.badge: {
                    "name": beacon.name,
                    "key": beacon.key,
                    "id": beacon.id,
                    "active": beacon.active
                } for beacon in self.beacons.all()
            },
            'beacons': {
                beacon.name: beacon.to_dict() for beacon in self.beacons.all()
            }
        }



class Hub(BaseModel):
    """Definition of a Hub, which is owned by a Project and has am externally generated uuid"""

    name = models.CharField(max_length=64)
    """Human readable identifier for this Hub (South Conference Room)"""

    project = models.ForeignKey(Project, null=True, related_name="hubs")

    god = models.BooleanField(default=False)

    uuid = models.CharField(max_length=64, db_index=True, unique=True)
    """ng-device generated uuid"""

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    """IP address of the hub (if relevant)"""

    last_seen_ts = models.DecimalField(max_digits=20, decimal_places=3, default=Decimal(0))
    """The last time the hub was seen by the server (in epoch time)"""
    
    last_hub_time_ts = models.DecimalField(max_digits=20, decimal_places=3, default=Decimal(0))
    """ The clock time of the hub at the time of the last API request """


    def get_object(self, last_update = None):
        if last_update:
            return {
                "name": self.name,
                "meetings": self.get_completed_meetings(),
                "is_god": self.god,
                'badge_map': {
                    member.badge: {
                        "name": member.name,
                        "key": member.key,
                        "id": member.id,
                        "observed_id": member.observed_id,
                        "active":member.active
                    } for member in self.project.members.all()
                        if int(member.date_updated.strftime("%s")) > last_update
                },
                'members': {
                    member.name: member.to_dict() for member in self.project.members.all()
                            if int(member.date_updated.strftime("%s")) > last_update},
                }

        else:
            return {
                "name": self.name,
                "meetings": self.get_completed_meetings(),
                "is_god": self.god
            }

    def get_completed_meetings(self):
        # TODO: returns all meetings, not just completed meetings.
        # need to change name to match functionality but don't want to break anything...
        return {
            meeting.key: {
                "last_log_timestamp": meeting.last_update_timestamp,
                "last_log_serial": meeting.last_update_index,
                "is_complete": meeting.is_complete,
                "uuid": meeting.uuid
            } for meeting in self.meetings.all()
        }

    def __unicode__(self):
        """This method is called in the drop-down for choosing the hub a project is associated with"""
        return unicode(self.name)



class Member(BaseModelMinimal):

    """Definition of a Member, who belongs to a Project, and owns a badge"""
    id = models.PositiveSmallIntegerField(primary_key=True, editable=False, unique=True, blank=True, validators=[MaxValueValidator(15999), MinValueValidator(1)])
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=64)
    badge = models.CharField(max_length=64, unique=True)
    observed_id = models.PositiveSmallIntegerField(default=0)
    active = models.BooleanField(default=True)
    comments = models.CharField(max_length=240, blank=True, default='')


    last_audio_ts = models.DecimalField(max_digits=20, decimal_places=3, default=_now_as_epoch)
    last_audio_ts_fract = models.DecimalField(max_digits=20, decimal_places=3, default=Decimal(0))
    last_proximity_ts = models.DecimalField(max_digits=20, decimal_places=3, default=_now_as_epoch)
    last_contacted_ts = models.DecimalField(max_digits=20, decimal_places=3, default=Decimal(0))
    last_unsync_ts = models.DecimalField(max_digits=20, decimal_places=3, default=Decimal(0))
    last_voltage = models.DecimalField(max_digits=5, decimal_places=3, default=Decimal(0))
    last_seen_ts = models.DecimalField(max_digits=20, decimal_places=3, default=Decimal(0))

    project = models.ForeignKey(Project, related_name="members")

    def get_project_id(self):
        return self.project.advertisment_project_id


    def generate_id(self):
        if not self.id:
            last_member = Member.objects.all().order_by('id').last()
            if not last_member:
                self.id = 1
            else:
                self.id = last_member.id + 1


    def save(self, *args, **kwargs):
        self.generate_id()
        super(Member, self).save(*args, **kwargs)


    @classmethod
    def datetime_to_epoch(cls, d):
        """
        Converts given datetime to epoch seconds and ms
        :param d: datetime
        :return:
        """
        epoch_seconds = (d - datetime.datetime(1970, 1, 1)).total_seconds()
        long_epoch_seconds = long(floor(epoch_seconds))
        ts_fract = d.microsecond / 1000;
        return (long_epoch_seconds, ts_fract)

    @classmethod
    def now_utc_epoch(cls):
        """
        Returns current UTC as epoch seconds and ms
        :return: long_epoch_seconds, ts_fract
        """
        return cls.datetime_to_epoch(timezone.datetime.now_utc())

    def to_dict(self):
        return dict(id=self.id,
                    name=self.name,
                    badge=self.badge
                    )

    def __unicode__(self):
        return unicode(self.name)

           



class Beacon(BaseModelMinimal):
    """docstring for Beacon"""
    id = models.PositiveSmallIntegerField(primary_key=True, editable=False, unique=True, blank=True, validators=[MaxValueValidator(32000), MinValueValidator(16000)])
    name = models.CharField(max_length=64)
    badge = models.CharField(max_length=64, unique=True)
    observed_id = models.PositiveSmallIntegerField(default=0)
    active = models.BooleanField(default=True)
    comments = models.CharField(max_length=240, blank = True ,default='')

    last_voltage = models.DecimalField(max_digits=5, decimal_places=3, default=Decimal(0))
    last_seen_ts = models.DecimalField(max_digits=20, decimal_places=3, default=Decimal(0))

    project = models.ForeignKey(Project, related_name="beacons")

    def generate_id(self):
        if not self.id:
            last_beacon = Beacon.objects.all().order_by('id').last()
            if not last_beacon:
                self.id = 16000
            else:
                self.id = last_beacon.id + 1


    def save(self, *args, **kwargs):
        self.generate_id()
        super(Beacon, self).save(*args, **kwargs)




    def get_project_id(self):
        return self.project.advertisment_project_id

    def to_dict(self):
        return dict(id=self.id,
                    name=self.name,
                    badge=self.badge
                    )

    def __unicode__(self):
        return unicode(self.name)
           


        


class Meeting(BaseModel):
    """
    Represents a Meeting, which belongs to a Project, and has a log_file and a last_update_time, among other standard
    metadata
    """

    version = models.DecimalField(decimal_places=2, max_digits=5)

    uuid = models.CharField(max_length=64, db_index=True, unique=True)
    """this will be something the phone can generate and give us, like [hub_uuid]-[start_time]"""

    start_time = models.DecimalField(decimal_places=3, max_digits= 20, null=True)
    """time they hit start"""

    end_time = models.DecimalField(decimal_places=3, max_digits= 20, null=True, blank=True)
    """time that they either hit end, or that the meeting timesout."""

    last_update_timestamp = models.DecimalField(decimal_places=3, max_digits= 20, null=True, blank=True)
    """log_timestamp of the last chunk received"""

    last_update_index = models.IntegerField(null=True, blank=True)
    """Serial Number of last log chunk received. Better be continuous!!"""

    ending_method = models.CharField(max_length=16, blank=True, null=True)
    """what caused the meeting to end? timeout|manual"""

    is_complete = models.BooleanField(default=False, blank=True)
    """whether we've gotten a signal that the meeting is complete (end_time != null?)"""

    log_file = models.FileField(upload_to=upload_to, storage=OverwriteStorage(), blank=True)
    """Local reference to log file"""
    project = models.ForeignKey(Project, related_name="meetings")
    """The Project this Meeting belongs to"""

    hub = models.ForeignKey(Hub, related_name="meetings")
    """Used when checking if there are meetings we don't have"""

    def __unicode__(self):
        return unicode(self.project.name + "|" + str(self.start_time))

    def get_chunks(self):
        """open and read this meeting's log_file"""

        chunks = []

        f = self.log_file

        f.readline()  # the first line will be info about the meeting
        

        for line in f.readlines():
            try:
                chunk = simplejson.loads(line)
                chunks.append(chunk)
            except Exception:
                #TODO this means we have some broken data or something,
                # do we want to log an error or do something about it
                pass

        f.seek(0)
        return chunks

    def get_meta(self):
        """return the metadata for this meeting object"""

        f = self.log_file
        meta = simplejson.loads(f.readline())
        line_type = meta["type"]
        meta["members"] = []

        # the following few lines are members joining
        line = simplejson.loads(f.readline())
        #TODO meetings with no data break this
        while "received" not in line["type"] and "ended" not in line["type"]:
            if "member" in line["type"] and line["data"]["change"] == "join":
                meta["members"].append(line["data"]["member_key"])
            try:
                line = simplejson.loads(f.readline())
            except ValueError as e:
                break

        #grab some additional metadata from the object
        meta['key'] = self.key
        meta['log_index'] = self.last_update_index
        meta['log_timestamp'] = self.last_update_timestamp
        meta['is_complete'] = self.is_complete
        meta['project'] = self.project.key

        if self.is_complete:
            meta['end_time'] = float(self.end_time)

        #return file pointer to beginning
        f.seek(0)
        return meta

    def to_object(self, file):
        """Get an representation of this object for use with HTTP responses"""

        meta = self.get_meta()

        if file:
            return {
                "chunks": self.get_chunks(),
                "metadata":meta
            }

        return { "metadata": meta }

class DataFile(BaseModel):
    """
    Manage a single data file - data is provided by the Python Hubs
    """

    uuid = models.CharField(max_length=64, db_index=True, unique=True)
    """this will be a concatenation of the hub uuid and data type"""

    data_type = models.CharField(max_length=64)
    """Is this an audio or proximity data log?"""

    # at this point we don't even really care about this, maybe worth storing though
    last_update_timestamp = models.DecimalField(
        decimal_places=3,
        max_digits= 20,
        null=True,
        blank=True)
    """Log_timestamp of the last chunk received"""

    filepath = models.CharField(max_length=65, unique=True, blank=True)
    """Local reference to log file"""

    hub = models.ForeignKey(Hub, related_name="data")
    """The Hub this DataFile belongs to"""

    project = models.ForeignKey(Project, null=True, related_name="data")
    """The Project this DataFile belongs to"""

    def __unicode__(self):
        return unicode(self.hub.name + "_" + str(self.data_type) + "_data")

    def get_meta(self):
        """creates a json object of the metadata for this DataFile"""
        return {
            'last_update_index': self.last_update_index,
            'log_timestamp': self.last_update_timestamp,
            'hub': self.hub.name
        }


    def to_object(self, file):
        """Get a representation of this object for use with HTTP responses"""
        if file:
            return {
                "chunks": self.get_chunks(),
                "metadata": self.get_meta()
            }
        else:
            return { "metadata": meta }
    
