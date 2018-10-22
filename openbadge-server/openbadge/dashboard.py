from controlcenter import Dashboard, widgets
from .models import Member, Unsync, Hub, Beacon
from django.conf import settings 
from django.db.models import Count
import time


def hours_to_secs(hrs):
    return hrs * 60 * 60

def secs_to_hours(secs):
    return (secs / 60) / 60

def secs_to_minutes(secs):
    return round((secs / 60), 1)

def cutoff_to_ts(cutoff):
    # cutoff is in hours
    return time.time() - hours_to_secs(cutoff)

# TODO filter by project??

class LowVoltageMembers(widgets.ItemList):
    model = Member
    queryset = model.objects.filter(active=True).filter(last_voltage__lt=settings.LOW_VOLTAGE).order_by('last_voltage')
    list_display = ('id', 'key', 'last_seen_ts', 'last_voltage', 'last_unsync_ts')
    width = widgets.LARGE
    sortable = True
    limit_to = None
    height = 400


class ManyResetMembers(widgets.ItemList):
    model = Unsync
    title = "MEMBERS WITH MULTIPLE RESETS WITHIN {} HOURS".format(settings.UNSYNC_CUTOFF_HOURS)
    width = widgets.LARGE
    # members have many unsyncs that are related to them
    # unsyncs have a timestamp and the member that unsynced
    # we need all members with > x number of unsyncs since y
    # width = widgets.FULL
    sortable = True
    
    cutoff_ts = cutoff_to_ts(settings.UNSYNC_CUTOFF_HOURS)
    # get all unsyncs since cutoff
    queryset = (model.objects
            .filter(unsync_ts__gt=cutoff_ts)
            .values('member__id', 'member__key', 'member__name', 'member__last_voltage')
            .annotate(num_unsyncs=Count('member__id'))
            .filter(num_unsyncs__gte=settings.NUM_UNSYNCS)
            .order_by('-num_unsyncs'))

    list_display = ('member__id', 'member__key', 'member__name', 'num_unsyncs', 'member__last_voltage')


class ThingNotSeen(widgets.ItemList):
    limit_to = None
    width = widgets.LARGE
    sortable = True

    def minutes_since_last_seen(self, obj):
        if (obj.last_seen_ts and obj.last_seen_ts != 0):
            return secs_to_minutes(time.time() - round(obj.last_seen_ts, 1))
        else:
            return "Not yet seen"

    minutes_since_last_seen.short_description = "minutes since last seen"
    minutes_since_last_seen.allow_tags = True

class HubsNotSeen(ThingNotSeen):
    model = Hub
    title = "HUBS NOT SEEN IN {} HOURS".format(settings.LAST_SEEN_CUTOFF_SHORT_HOURS)
    cutoff_ts = cutoff_to_ts(settings.LAST_SEEN_CUTOFF_SHORT_HOURS)
    queryset = model.objects.filter(last_seen_ts__lt=cutoff_ts)
    list_display = ('id', 'key', 'last_seen_ts', 'minutes_since_last_seen')


class BeaconsNotSeen(ThingNotSeen):
    model = Beacon
    title = "BEACONS NOT SEEN IN {} HOURS".format(settings.LAST_SEEN_CUTOFF_SHORT_HOURS)
    cutoff_ts = cutoff_to_ts(settings.LAST_SEEN_CUTOFF_SHORT_HOURS)
    queryset = model.objects.filter(last_seen_ts__lt=cutoff_ts).filter(active=True).order_by('last_seen_ts')
    list_display = ('id', 'key', 'last_seen_ts', 'last_voltage', 'minutes_since_last_seen')


class MembersNotSeenShort(ThingNotSeen):
    model = Member
    title = "MEMBERS NOT SEEN IN {} HOURS".format(settings.LAST_SEEN_CUTOFF_SHORT_HOURS)
    # cutoff is in hours
    cutoff_ts = cutoff_to_ts(settings.LAST_SEEN_CUTOFF_SHORT_HOURS)
    queryset = model.objects.filter(last_seen_ts__lt=cutoff_ts).filter(active=True).order_by('last_seen_ts')
    list_display = ('id', 'key', 'last_seen_ts', 'minutes_since_last_seen', 'last_voltage', 'last_unsync_ts')


class MembersNotSeenLong(ThingNotSeen):
    model = Member
    title = "MEMBERS NOT SEEN IN {} HOURS".format(settings.LAST_SEEN_CUTOFF_LONG_HOURS)
    cutoff_ts = cutoff_to_ts(settings.LAST_SEEN_CUTOFF_LONG_HOURS)
    queryset = model.objects.filter(last_seen_ts__lt=cutoff_ts).filter(active=True).order_by('last_seen_ts')
    list_display = ('id', 'key', 'last_seen_ts', 'minutes_since_last_seen', 'last_voltage', 'last_unsync_ts')

class MembersAll(ThingNotSeen):
    model = Member
    title = "ALL MEMBERS"
    queryset = model.objects.filter(active=True)
    list_display = ('id', 'key', 'last_seen_ts',  'last_voltage', 'last_unsync_ts', 'minutes_since_last_seen')



class BadgeDashboard(Dashboard):
    widgets = (
        ManyResetMembers,
        LowVoltageMembers,
        (MembersNotSeenShort, MembersNotSeenLong, MembersAll),
        BeaconsNotSeen,
        HubsNotSeen
    )
