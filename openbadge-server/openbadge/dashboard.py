from controlcenter import Dashboard, widgets
from .models import Member, Unsync, Hub, Beacon
from django.conf import settings
from django.db.models import Count
from datetime import datetime
import time
import pytz
from pytz import timezone


def hours_to_secs(hrs):
    return hrs * 60 * 60

def secs_to_hours(secs):
    return (secs / 60) / 60

def secs_to_minutes(secs):
    return round((secs / 60), 1)

def cutoff_to_ts(cutoff):
    # cutoff is in hours
    return time.time() - hours_to_secs(cutoff)

def timestamp_to_date(ts):
    return (pytz.utc.localize(datetime.utcfromtimestamp(ts))
                .astimezone(timezone(settings.TIME_ZONE))
                .strftime('%Y-%m-%d %H:%M:%S %Z'))



class BaseItemList(widgets.ItemList):

    def last_seen_date(self, obj):
        if (obj.last_seen_ts is not None and obj.last_seen_ts != 0):
            return timestamp_to_date(int(obj.last_seen_ts))
        else:
            return "Not yet seen"

    last_seen_date.short_description = "Last Seen"

    def last_unsync_date(self, obj):
        if (obj.last_unsync_ts is not None and obj.last_unsync_ts != 0):
            return timestamp_to_date(int(obj.last_unsync_ts))
        else:
            return "No Unsyncs Recorded"

    last_unsync_date.short_description = "Last Unsync"

class LowVoltageMembers(BaseItemList):

    model = Member
    list_display = ('id', 'key', 'name', 'last_seen_date', 'last_voltage', 'last_unsync_date')
    width = widgets.LARGE
    sortable = True
    limit_to = None
    height = 400

    def get_queryset(self):
        return (self.model.objects
                .filter(active=True)
                .filter(last_voltage__lt=settings.LOW_VOLTAGE)
                .order_by('last_voltage'))


class ManyResetMembers(BaseItemList):
    model = Unsync
    title = "MEMBERS WITH MULTIPLE RESETS WITHIN {} HOURS".format(settings.UNSYNC_CUTOFF_HOURS)
    width = widgets.LARGE
    # members have many unsyncs that are related to them
    # unsyncs have a timestamp and the member that unsynced
    # we need all members with > x number of unsyncs since y
    # width = widgets.FULL
    sortable = True

    # get all unsyncs since cutoff
    def get_queryset(self):
        return (self.model.objects
                .filter(unsync_ts__gt=cutoff_to_ts(settings.UNSYNC_CUTOFF_HOURS))
                .values('member__id', 'member__key', 'member__name', 'member__last_voltage')
                .annotate(num_unsyncs=Count('member__id'))
                .filter(num_unsyncs__gte=settings.NUM_UNSYNCS)
                .order_by('-num_unsyncs'))

    list_display = ('member__id', 'member__key', 'member__name', 'num_unsyncs', 'member__last_voltage')


class ThingNotSeen(BaseItemList):
    limit_to = None
    width = widgets.LARGE
    sortable = True

    def minutes_since_last_seen(self, obj):
        if (obj.last_seen_ts and obj.last_seen_ts != 0):
            return secs_to_minutes(time.time() - int(obj.last_seen_ts))
        else:
            return "Not yet seen"

    def cutoff_long(self):
        return cutoff_to_ts(settings.LAST_SEEN_CUTOFF_LONG_HOURS)

    def cutoff_short(self):
        return cutoff_to_ts(settings.LAST_SEEN_CUTOFF_SHORT_HOURS)

    minutes_since_last_seen.short_description = "minutes since last seen"

class HubsNotSeen(ThingNotSeen):
    model = Hub
    title = "HUBS NOT SEEN IN {} HOURS".format(settings.LAST_SEEN_CUTOFF_SHORT_HOURS)
    list_display = ('id', 'key', 'name', 'last_seen_date', 'minutes_since_last_seen')

    def get_queryset(self):
        return self.model.objects.filter(last_seen_ts__lt=self.cutoff_short())


class BeaconsNotSeen(ThingNotSeen):
    model = Beacon
    title = "BEACONS NOT SEEN IN {} HOURS".format(settings.LAST_SEEN_CUTOFF_SHORT_HOURS)
    list_display = ('id', 'key', 'name', 'last_seen_date', 'last_voltage', 'minutes_since_last_seen')

    def get_queryset(self):
        return (self.model.objects
                .filter(last_seen_ts__lt=self.cutoff_short())
                .filter(active=True)
                .order_by('last_seen_ts'))


class MembersNotSeenShort(ThingNotSeen):
    model = Member
    title = "MEMBERS NOT SEEN IN {} HOURS".format(settings.LAST_SEEN_CUTOFF_SHORT_HOURS)
    list_display = ('id', 'key', 'name', 'last_seen_date', 'minutes_since_last_seen', 'last_voltage', 'last_unsync_date')

    def get_queryset(self):
        return (self.model.objects
                .filter(last_seen_ts__lt=self.cutoff_short())
                .filter(active=True)
                .order_by('last_seen_ts'))


class MembersNotSeenLong(ThingNotSeen):
    model = Member
    title = "MEMBERS NOT SEEN IN {} HOURS".format(settings.LAST_SEEN_CUTOFF_LONG_HOURS)
    list_display = ('id', 'key', 'name', 'last_seen_date', 'minutes_since_last_seen', 'last_voltage', 'last_unsync_date')

    def get_queryset(self):
        return (self.model.objects
                .filter(last_seen_ts__lt=self.cutoff_long())
                .filter(active=True)
                .order_by('last_seen_ts'))


class MembersAll(ThingNotSeen):
    model = Member
    title = "ALL MEMBERS"
    list_display = ('id', 'key', 'name', 'last_seen_date', 'minutes_since_last_seen', 'last_voltage', 'last_unsync_date')

    def get_queryset(self):
        return self.model.objects.filter(active=True)


class BadgeDashboard(Dashboard):
    widgets = (
        ManyResetMembers,
        LowVoltageMembers,
        (MembersNotSeenShort, MembersNotSeenLong, MembersAll),
        BeaconsNotSeen,
        HubsNotSeen
    )
