from django.conf.urls import include, url
from . import views
from django.views.generic.base import TemplateView

urlpatterns = [
    # # APP URLs. DO NOT TOUCH THESE
    # url(r'^get_group/(?P<group_key>\w+)/$', views.get_group, name='get_group'),
    # url(r'^get_finished_meetings/(?P<group_key>\w+)/$', views.get_finished_meetings, name='get_finished_meetings'),
    # url(r'^log_data/$', views.log_data, name='log_data'),

    # No-Groups URLS
    url(r'^projects$', views.projects, name='projects'),
    url(r'^(?P<project_id>\w+)/meetings$', views.meetings, name='meetings'),
    url(r'^(?P<project_id>\w+)/hubs$', views.hubs, name='hubs'),
    url(r'^(?P<project_id>\w+)/members', views.members, name='members'),

    # Reports
    # url(r'^internal_report/$', views.internal_report, name='internal_report'),
    # url(r'^weekly_group_report/(?P<group_key>\w+)/(?P<week_num>[0-9]+)$', views.weekly_group_report, name='weekly_group_report'),
]