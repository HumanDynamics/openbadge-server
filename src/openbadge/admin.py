from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django import forms

import fields, csv, zipfile, os, uuid, errno, datetime
import simplejson, pytz
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.admin.widgets import AdminTextareaWidget, AdminTextInputWidget
from django.template.loader import render_to_string

from django.utils.translation import ugettext_lazy as _

from django.db.models import Count, Case, When, IntegerField, Sum
from django.conf import settings
from django import utils

from .models import OpenBadgeUser, StudyGroup, StudyMember, Meeting, VisualizationRange, WeeklyGroupReport


def register(model):
    def inner(admin_class):
        admin.site.register(model,admin_class)
        return admin_class

    return inner

@register(OpenBadgeUser)
class OpenBadgeUserAdmin(auth_admin.UserAdmin):
    list_display = auth_admin.UserAdmin.list_display

    fieldsets = auth_admin.UserAdmin.fieldsets + (
        (_('OpenBadge User Data'), {'fields': ()}),
    )




class SerializedFieldWidget(AdminTextareaWidget):

    def render(self, name, value, attrs=None):
        return super(SerializedFieldWidget, self).render(name, simplejson.dumps(value, indent=4), attrs)


class StudyMemberInline(admin.TabularInline):
    model = StudyMember
    readonly_fields = ("key",)
    extra = 3


class VisualizationRangeInline(admin.TabularInline):
    model = VisualizationRange
    extra = 3

class MeetingsInLine(admin.TabularInline):
    model = Meeting
    readonly_fields = ("uuid",)


@register(StudyGroup)
class StudyGroupAdmin(admin.ModelAdmin):
    readonly_fields = ("key",)
    list_display = ('name', 'key', 'members_list', 'number_of_members', 'number_of_meetings', 'total_hours_spend_meeting', 'visualization_enabled',)
    list_filter = ('name', )
    inlines = (StudyMemberInline, VisualizationRangeInline, MeetingsInLine)
    actions_on_top = True

    def get_queryset(self, request):
        return StudyGroup.objects.prefetch_related("members", "visualization_ranges")

    def members_list(self, inst):
        return ", ".join([member.name for member in inst.members.all()])
    #members_list.admin_order_field = 'members_list'

    def number_of_members(self, inst):
        return len(inst.members.all())

    def number_of_meetings(self, inst):
        if inst.meetings.all():
            return len([meeting.uuid for meeting in inst.meetings.all()])
        return "NONE"
    #number_of_meetings.admin_order_field = 'number_of_meetings' #Allows column order sorting
    #number_of_meetings.short_description = 'Number of Meetings' #Renames column head

    def total_hours_spend_meeting(self, inst):
        if inst.meetings.all():
            return int(sum([(meeting.end_time - meeting.start_time).total_seconds()/3600 for meeting in inst.meetings.all()]))
        return "NONE"

    def visualization_enabled(self, inst):
        now = datetime.datetime.utcnow()
        now = now.replace(tzinfo=pytz.utc)
        for r in inst.visualization_ranges.all():
            if r.start <= now and r.end >= now:
                return True
        return False
    visualization_enabled.admin_order_field = 'visualization_enabled'
    visualization_enabled.boolean = True

@register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    readonly_fields = ("key",)
    list_display = ('uuid', 'group', 'start_time', 'end_time', 'duration', 'moderator', 'type', 'location', 'show_visualization', 'is_complete')
    actions_on_top = True
    
    def duration(self, inst):
        return inst.end_time - inst.start_time

@register(WeeklyGroupReport)
class WeeklyGroupReportAdmin(admin.ModelAdmin):
    readonly_fields = ('group_key','week_num','start_date','end_date','total_meeting_count','total_duration_of_meetings','avg_speaking_time','longest_meeting_date',)
    list_display = ('group_key','week_num','start_date','end_date','total_meeting_count','total_duration_of_meetings','avg_speaking_time','longest_meeting_date')
    list_filter = ('group_key', )
