from django.conf.urls import include, url
from . import views
from django.views.generic.base import TemplateView

badges_list = views.MemberViewSet.as_view({
    'get': 'list',
    # 'post': 'create',
})

badges_details = views.MemberViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
})

hubs_list = views.HubViewSet.as_view({
    'get': 'list',
    # 'post': 'create',
})


hubs_details = views.HubViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
})

urlpatterns = [
    # # APP URLs. DO NOT TOUCH THESE
    # url(r'^get_group/(?P<group_key>\w+)/$', views.get_group, name='get_group'),
    # url(r'^get_finished_meetings/(?P<group_key>\w+)/$', views.get_finished_meetings, name='get_finished_meetings'),
    # url(r'^log_data/$', views.log_data, name='log_data'),

    # No-Groups URLS
    url(r'^projects$', views.projects, name='projects'),
    url(r'^(?P<project_key>\w+)/meetings$', views.meetings, name='meetings'),
    url(r'^(?P<project_key>\w+)/hubs$', views.hubs, name='hubs'),
    url(r'^(?P<project_key>\w+)/members', views.members, name='members'),
    url(r'^(?P<project_key>\w+)/datalogs', views.datalogs, name='datalogs'),

    url(r'^badges/$', badges_list, name='badge-list'),
    url(r'badges/(?P<key>\w+)', badges_details, name='badge-details'),

    url(r'^hubs/$', hubs_list, name='hub-list'),
    #url(r'hubs/(?P<name>\w+)', hubs_details, name='hub-details'),
    url(r'hubs/(?P<name>[\w-]+)', hubs_details, name='hub-details'),
    url(r'hubs/(?P<name>[\w-]+)/upload', hubs_details, name='hub-details'),


    # Reports
    # url(r'^internal_report/$', views.internal_report, name='internal_report'),
    # url(r'^weekly_group_report/(?P<group_key>\w+)/(?P<week_num>[0-9]+)$', views.weekly_group_report, name='weekly_group_report'),
]
