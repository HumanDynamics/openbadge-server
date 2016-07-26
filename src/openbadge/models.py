# coding=utf-8
import datetime
import os
import pytz
import random
import simplejson
import string

from django.conf import settings
from django.contrib.auth import models as auth_models
from django.core.files.storage import FileSystemStorage
from django.db import models


def key_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class BaseModel(models.Model):
    """
    Base model from which all other models should inherit. It has a unique key and other nice fields, like a unique id.
    If you override this class, you should probably add more unique identifiers, like a uuid or hash or something.
    """
    id = models.AutoField(primary_key=True)
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


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name):
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


##########################################################################################


@fix_email
class OpenBadgeUser(auth_models.AbstractUser, BaseModel):
    pass


def _to_timestamp(dt):
    return (dt - datetime.datetime(1970, 1, 1).replace(tzinfo=pytz.UTC)).total_seconds()


def upload_to(self, filename):
    return "/".join(('logs', str(self.project.name), self.uuid + os.path.splitext(filename)[1]))


class Project(BaseModel):
    """
    Definition of the Project, which is an `organization`-level collection of hubs, badges, and meetings
    """

    name = models.CharField(max_length=64)
    """Human readable identifier for this project (Apple, Google, etc.)"""

    def __unicode__(self):
        return self.name

    def get_meetings(self, file):
        return {'meetings': {meeting.uuid: meeting.to_object(file) for meeting in self.meetings.all()}}

    def to_object(self):
        """for use in HTTP responses, gets the id, name, members, and a map form badge_ids to member names"""

        return {'project_id': self.id,
                'name': self.name,
                'badge_map': {member.badge: {"name": member.name, "key": member.key} for member in self.members.all()},
                'members': {member.name: member.to_dict() for member in self.members.all()}
                }


class Hub(BaseModel):
    """Definition of a Hub, which is owned by a Project and has am externally generated uuid"""

    name = models.CharField(max_length=64)
    """Human readable identifier for this Hub (South Conference Room)"""

    project = models.ForeignKey(Project, null=True, related_name="hubs")

    god = models.BooleanField(default=False)

    uuid = models.CharField(max_length=64, db_index=True, unique=True)
    """ng-device generated uuid"""

    def get_object(self):
        return {"name": self.name, "meetings": self.get_completed_meetings(), "is_god": self.god}

    def get_completed_meetings(self):
        for meeting in self.meetings.all():
            if meeting.last_update_serial == -1:
                print "need to reparse file"
                try:
                    with open(meeting.log_file.file.name, "rb") as f:
                        f.seek(-2, 2)  # Jump to the second last byte.
                        while f.read(1) != b"\n":  # Until EOL is found...
                            f.seek(-2, 1)  # ...jump back the read byte plus one more.

                        last = f.readline()  # Read last line.
                    last_log = simplejson.loads(last)
                    meeting.last_update_serial = last_log['last_log_serial']
                    meeting.last_update_time = last_log['last_log_time']
                except IOError:
                    print "Error! File empty?"
                    meeting.last_update_serial = 0

                meeting.save()
        return {meeting.uuid: {"last_log_timestamp": meeting.last_update_time,
                               "last_log_serial": meeting.last_update_serial,
                               "is_complete": meeting.is_complete}
                for meeting in self.meetings.all()}

    def __unicode__(self):
        """This method is called in the drop-down for choosing the hub a project is associated with"""
        return self.name


class Member(BaseModel):
    """Definition of a Member, who belongs to a Project, and owns a badge"""

    name = models.CharField(max_length=64)
    email = models.EmailField(unique=True)
    badge = models.CharField(max_length=64)
    """Some sort of hub-readable ID for the badge, similar to a MAC, but accessible from iPhone"""

    project = models.ForeignKey(Project, related_name="members")

    def to_dict(self):
        return dict(id=self.id,
                    name=self.name,
                    badge=self.badge
                    )

    def __unicode__(self):
        return self.name


class Meeting(BaseModel):
    """
    Represents a Meeting, which belongs to a Project, and has a log_file and a last_update_time, among other standard
    metadata
    """

    uuid = models.CharField(max_length=64, db_index=True, unique=True)
    """this will be something the phone can generate and give us, like [hub_uuid]-[start_time]"""

    start_time = models.DateTimeField()
    """time they hit start"""

    end_time = models.DateTimeField(null=True, blank=True)
    """time that they either hit end, or that the meeting timesout."""

    last_update_time = models.FloatField(null=True, blank=True)
    """log_timestamp of the last chunk received"""

    last_update_serial = models.IntegerField(null=True, blank=True)
    """Serial Number of last log chunk received. Better be continuous!!"""

    ending_method = models.CharField(max_length=16, blank=True, null=True)
    """what caused the meeting to end? timeout|manual"""

    # random meeting user-submitted data
    type = models.CharField(max_length=32)
    location = models.CharField(max_length=32)
    description = models.TextField(blank=True)

    is_complete = models.BooleanField(default=False, blank=True)
    """whether we've gotten a signal that the meeting is complete (end_time != null?)"""

    log_file = models.FileField(upload_to=upload_to, storage=OverwriteStorage(), blank=True)
    """Local reference to log file"""

    project = models.ForeignKey(Project, related_name="meetings")
    """The Project this Meeting belongs to"""

    hub = models.ForeignKey(Hub, related_name="meetings")
    """Used when checking if there are meetings we don't have"""

    def __unicode__(self):
        return unicode(self.project.name) + "|" + str(self.start_time)

    def get_chunks(self):
        """open and read this meeting's log_file"""

        chunks = []

        f = self.log_file

        f.readline()  # the first line will be info about the meeting, all subsequent lines are chunks

        for line in f.readlines():
            try:
                chunk = simplejson.loads(line)
                chunks.append(chunk)
            except Exception:
                pass

        f.seek(0)
        return chunks

    def get_meta(self):
        """open and read the first line of this meeting's log_file"""

        f = self.log_file
        return simplejson.loads(
            f.readline())  # the first line will be info about the meeting, all subsequent lines are chunks

    def get_last_sample_time(self):
        """Reads this meetings log file and gets the timestamp of the last received chunk."""

        chunks = self.get_chunks()

        if not chunks:
            return (self.start_time, None)

        chunk = chunks[-1]
        # print len(chunks), chunk
        start_timestamp = chunk['timestamp']
        start_timestamp += chunk['timestamp_ms'] / 1000.0 if 'timestamp_ms' in chunk else 0
        sample_duration = chunk['sampleDelay'] / 1000.0 if 'sampleDelay' in chunk else 0
        num_samples = len(chunk['samples']) if 'samples' in chunk else 0

        end_timestamp = start_timestamp + sample_duration * num_samples

        return datetime.datetime.fromtimestamp(end_timestamp), start_timestamp

    def to_object(self, file):
        """Get an representation of this object for use with HTTP responses"""
        if file:
            return {"chunks": self.get_chunks(),
                    "metadata": self.get_meta()}

        return {"metadata": self.get_meta()}

# class SamplesDataChunk(models.Model):
#     badge = models.ForeignKey(Badge)
#     time  = models.DateTimeField()
#     samples = models.CommaSeparatedIntegerField()
#
#     def to_dict(self):
#         return dict(badge = self.badge,
#                     time = self.time,
#                     samples = self.samples)
#
#
# class ActionDataChunk(models.Model):
#     action = models.CharField(max_length=64)
#     time  = models.DateTimeField()
#     member = models.ForeignKey(Badge, null=True)
#
#     def to_dict(self):
#         return dict(action = self.action,
#                     time = self.time,
#                     member = self.member)
