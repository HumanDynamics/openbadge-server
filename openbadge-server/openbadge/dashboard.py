from controlcenter import Dashboard, widgets
from .models import Member, Unsync, Hub, Beacon
from django.conf import settings 
from django.db.models import Count
import time


def hours_to_secs(hrs):
    return hrs * 60 * 60


def cutoff_to_ts(cutoff):
    # cutoff is in hours
    return time.time() - hours_to_secs(cutoff)

# TODO filter by project??

class LowVoltageMembers(widgets.ItemList):
    model = Member
    queryset = model.objects.filter(last_voltage__lt=settings.LOW_VOLTAGE)
    list_display = ('id', 'key', 'last_seen_ts', 'last_voltage', 'last_unsync_ts')
    width = widgets.FULL
    sortable = True
    limit_to = 0
    height = 400


class ManyResetMembers(widgets.ItemList):
    model = Unsync
    # members have many unsyncs that are related to them
    # unsyncs have a timestamp and the member that unsynced
    # we need all members with > x number of unsyncs since y
    width = widgets.FULL
    sortable = True
    
    # TODO try starting with 2 in 24 hrs
    # TODO show all badges sorted by num resets in last 24hrs
    cutoff_ts = cutoff_to_ts(settings.UNSYNC_CUTOFF)
    # get all unsyncs since cutoff
    queryset = (model.objects.filter(unsync_ts__gt=cutoff_ts)
                .annotate(member_unsyncs=Count('member__name'))
                .filter(member_unsyncs__gte=settings.NUM_UNSYNCS)
                .order_by('member_unsyncs'))

    list_display = ('member__id', 'member__key', 'member__name', 'member_unsyncs', 'last_voltage')


class HubsNotSeen(widgets.ItemList):
    model = Hub
    sortable = True
    cutoff_ts = cutoff_to_ts(settings.LAST_SEEN_CUTOFF)
    queryset = model.objects.filter(last_seen_ts=cutoff_ts)
    list_display = ('id', 'key', 'last_seen_ts')
    width = widgets.FULL

    # TODO add 'ago' field ex. seen 20 mins ago

class BeaconsNotSeen(widgets.ItemList):
    model = Beacon
    width = widgets.FULL
    sortable = True
    # TODO ignore inactive
    cutoff_ts = cutoff_to_ts(settings.LAST_SEEN_CUTOFF)
    queryset = model.objects.filter(last_seen_ts__lt=cutoff_ts)
    list_display = ('id', 'key', 'last_seen_ts', 'last_voltage')


class MembersNotSeen(widgets.ItemList):
    model = Member
    width = widgets.FULL
    sortable = True
    # TODO more than 2, 6 hrs, less than 1 week
    # ignore inactive
    # also tab to see all
    cutoff_ts = cutoff_to_ts(settings.LAST_SEEN_CUTOFF)
    queryset = model.objects.filter(last_seen_ts__lt=cutoff_ts)
    list_display = ('id', 'key', 'last_seen_ts', 'last_voltage', 'last_unsync_ts')


class BadgeDashboard(Dashboard):
    widgets = (
        ManyResetMembers,
        MembersNotSeen,
        BeaconsNotSeen,
        HubsNotSeen,
        LowVoltageMembers
    )
