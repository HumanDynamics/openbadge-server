from django.conf.urls import include, url
from . import views
from django.views.generic.base import TemplateView

urlpatterns = [
    # APP URLs. DO NOT TOUCH THESE
    url(r'^get_group/(?P<group_key>\w+)/$', views.get_group, name='get_group'),
    url(r'^get_finished_meetings/(?P<group_key>\w+)/$', views.get_finished_meetings, name='get_finished_meetings'),
    url(r'^log_data/$', views.log_data, name='log_data'),

    # Reports
    url(r'^internal_report/$', views.internal_report, name='internal_report'),
    url(r'^weekly_group_report/(?P<group_key>\w+)/(?P<week_num>[0-9]+)$', views.weekly_group_report, name='weekly_group_report'),
    url(r'^h1_report/(?P<member_key>\w+)/$', views.h1_report, name='report'),
    url(r'^h2_report/(?P<member_key>\w+)/(?P<date>[0-9_-]+)/$', views.h2_daily_report, name='h2_report'),

    # API
    url(r'^api/groups/$', views.api_groups, name='api_groups'),
    url(r'^api/group/(?P<group_key>\w+)/$', views.api_group, name='api_group'),
    url(r'^api/meetings/$', views.api_meetings, name='api_meetings'),
    url(r'^api/meeting/(?P<uuid>\w+)/$', views.api_meeting, name='api_meeting'),
    url(r'^api/example_view/$', views.example_view, name='example_view'),

    # Forms
    url(r'^forms/h2_report/$', views.forms_h2_report),

]