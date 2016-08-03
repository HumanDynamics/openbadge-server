from datetime import datetime, timedelta

import simplejson
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextareaWidget
from django.contrib.auth import admin as auth_admin
from django.utils.translation import ugettext_lazy as _
from .models import OpenBadgeUser, Meeting, Member, Project, Hub


def register(model):
    def inner(admin_class):
        admin.site.register(model, admin_class)
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


class MemberInline(admin.TabularInline):
    model = Member
    readonly_fields = ("key",)
    extra = 3


class MeetingInLine(admin.TabularInline):
    model = Meeting
    readonly_fields = ("uuid",)


class HubInline(admin.TabularInline):
    model = Hub
    readonly_fields = ("key",)


@register(Project)
class ProjectAdmin(admin.ModelAdmin):
    readonly_fields = ("key",)
    list_display = ('name', 'key', 'id', 'number_of_members', 'number_of_meetings', 'total_meeting_hours')
    list_filter = ('name',)
    inlines = (MemberInline, HubInline, MeetingInLine)
    actions_on_top = True

    def get_queryset(self, request):
        return Project.objects.prefetch_related("members", "hubs")

    # def members_list(self, inst):
    #     return ", ".join([member.name for member in inst.members.all()])
    # #members_list.admin_order_field = 'members_list'

    @staticmethod
    def number_of_members(inst):
        return len(inst.members.all())

    @staticmethod
    def number_of_meetings(inst):
        if inst.meetings.all():
            return len([meeting.uuid for meeting in inst.meetings.all()])
        return "NONE"

    # number_of_meetings.admin_order_field = 'number_of_meetings' #Allows column order sorting
    # number_of_meetings.short_description = 'Number of Meetings' #Renames column head

    @staticmethod
    def total_meeting_hours(inst):
        if inst.meetings.all():
            def time_diff(x):
                return (x.end_time - x.start_time)

            return timedelta(seconds = sum(
                [time_diff(meeting) for meeting in inst.meetings.all() if meeting.end_time]) / 3600)
        return "NONE"


@register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    readonly_fields = ("key",)
    list_display = ('uuid', 'project_name', 'hub',
                    'start', 'end',
                    'last_update', 'last_update_index',
                    'duration',
                    'is_complete')
    actions_on_top = True

    def last_update(self, inst):
        if inst.last_update_timestamp:
            return datetime.fromtimestamp(inst.last_update_timestamp)

    def start(self, inst):
        if inst.start_time:
            return datetime.fromtimestamp(inst.start_time)

    def end(self, inst):
        if inst.end_time:
            return datetime.fromtimestamp(inst.end_time)


    def project_name(self, inst):
        return inst.project.name

    project_name.admin_order_field = 'project_name'
    project_name.short_description = 'Project'

    def duration(self, inst):
        return timedelta(seconds=inst.last_update_timestamp - inst.start_time)

    duration.admin_order_field = 'duration'
