from django.core.files.storage import FileSystemStorage
from django.db import models
from django.contrib.auth import models as auth_models
from django.db.models import Q, Sum

import string, random, os, math, datetime, pytz, simplejson

from .fields import SerializedDataField

from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver
from django.conf import settings

def key_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class BaseModel(models.Model):
    '''
    Base model from which all other models should inherit. It has a unique key and other nice fields
    '''
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


class StudyGroup(BaseModel):
    name = models.CharField(max_length=64, unique=True)

    def generate_key(self):
        return super(StudyGroup, self).generate_key(length=5)

    def to_dict(self):
        return dict(key=self.key,
                    name=self.name,
                    visualization_ranges=[r.to_dict() for r in self.visualization_ranges.all()],
                    members=[member.to_dict() for member in self.members.all()])

    def __unicode__(self):
        return self.name


def _to_timestamp(dt):
    return (dt - datetime.datetime(1970, 1, 1).replace(tzinfo=pytz.UTC)).total_seconds()


class VisualizationRange(models.Model):
    group = models.ForeignKey(StudyGroup, related_name="visualization_ranges")
    start = models.DateTimeField()
    end = models.DateTimeField()

    def to_dict(self):
        return dict(start=_to_timestamp(self.start),
                    end=_to_timestamp(self.end),
                    )


class StudyMember(BaseModel):
    name = models.CharField(max_length=64)
    email = models.EmailField(unique=True)
    badge = models.CharField(max_length=64)
    group = models.ForeignKey(StudyGroup, related_name="members")

    def to_dict(self):
        return dict(key=self.key,
                    name=self.name,
                    badge=self.badge,
                    )

    def __unicode__(self):
        return self.name


def upload_to(self, filename):
    return "/".join(('logs', self.group.key, self.uuid + os.path.splitext(filename)[1]))


class Meeting(BaseModel):
    uuid = models.CharField(max_length=64, db_index=True, unique=True)
    group = models.ForeignKey(StudyGroup, related_name="meetings")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    moderator = models.ForeignKey(StudyMember, null=True, blank=True)
    type = models.CharField(max_length=32)
    location = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    members = models.TextField(default="[]", blank=True)
    is_complete = models.BooleanField(default=False, blank=True)
    show_visualization = models.BooleanField(default=False, blank=True)
    log_file = models.FileField(upload_to=upload_to, storage=OverwriteStorage(), blank=True)
    ending_method = models.CharField(max_length=16, blank=True)

    def __unicode__(self):
        return unicode(self.group) + "|" + str(self.start_time)

    def get_chunks(self):
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

    def get_last_sample_time(self):

        chunks = self.get_chunks()

        if not chunks:
            return self.start_time

        chunk = chunks[-1]

        start_timestamp = chunk['timestamp']
        sample_duration = chunk['sampleDelay'] / 1000.0
        num_samples = len(chunk['samples'])

        end_timestamp = start_timestamp + sample_duration * num_samples

        return datetime.datetime.fromtimestamp(end_timestamp)

class WeeklyGroupReport(models.Model):
    group_key = models.CharField(max_length=32)
    week_num = models.CharField(max_length=32, default="none")    
    total_duration_of_meetings = models.CharField(max_length=32)
    longest_meeting_date = models.CharField(max_length=32)
    avg_speaking_time = models.CharField(max_length=32)
    total_meeting_count = models.CharField(max_length=32)
    start_date = models.CharField(max_length=32, default="none")
    end_date = models.CharField(max_length=32, default="none")

    def to_dict(self):
        return dict(group_key=self.group_key,
                    week_num=self.week_num,
                    total_duration_of_meetings=self.total_duration_of_meetings,
                    longest_meeting_date=self.longest_meeting_date,
                    avg_speaking_time=self.avg_speaking_time,
                    total_meeting_count=self.total_meeting_count,
                    start_date=self.start_date,
                    end_date=self.end_date
                    )
