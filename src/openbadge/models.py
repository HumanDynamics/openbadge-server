from django.core.files.storage import FileSystemStorage
from django.db import models
from django.contrib.auth import models as auth_models
from django.db.models import Q, Sum

import string, random, os, math

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

    def generate_key(self):
        if not self.key:
            for _ in range(10):
                key = key_generator(10)
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







##########################################################################################


@fix_email
class OpenBadgeUser(auth_models.AbstractUser, BaseModel):
    pass


class StudyGroup(BaseModel):
    name = models.CharField(max_length=64, blank=True)
    show_widget = models.BooleanField(blank=True)

    def to_dict(self):
        return dict(key=self.key,
                    name=self.name,
                    show_widget=self.show_widget,
                    members=[member.to_dict() for member in self.members.all()])


class StudyMember(BaseModel):
    name = models.CharField(max_length=64)
    email = models.EmailField()
    badge = models.CharField(max_length=64)
    group = models.ForeignKey(StudyGroup, related_name="members")

    def to_dict(self):
        return dict(key=self.key,
                    name=self.name,
                    badge=self.badge,
                    )


class Meeting(BaseModel):
    group = models.ForeignKey(StudyGroup)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    moderator = models.ForeignKey(StudyMember)
    type = models.CharField(max_length=32)
    description = models.TextField(blank=True)



