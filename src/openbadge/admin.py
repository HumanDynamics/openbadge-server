from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django import forms

import fields, csv, zipfile, os, uuid, errno
import simplejson
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.admin.widgets import AdminTextareaWidget, AdminTextInputWidget
from django.template.loader import render_to_string

from django.utils.translation import ugettext_lazy as _

from django.db.models import Count, Case, When, IntegerField, Sum
from django.conf import settings
from django import utils

from .models import OpenBadgeUser, StudyGroup, StudyMember, Meeting


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


@register(StudyGroup)
class StudyGroupAdmin(admin.ModelAdmin):
    readonly_fields = ("key",)
    list_display = ('name', 'key', 'members_list', 'show_widget',)
    list_editable = ('show_widget',)
    list_filter = ('name', 'show_widget')
    inlines = (StudyMemberInline,)
    actions_on_top = True

    def get_queryset(self, request):
        return StudyGroup.objects.prefetch_related("members")

    def members_list(self, inst):
        return ", ".join([member.name for member in inst.members.all()])
    members_list.admin_order_field = 'members_list'


@register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    readonly_fields = ("key",)
    list_display = ('group', 'start_time', 'end_time',)
    actions_on_top = True


