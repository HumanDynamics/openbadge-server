from django.conf.urls import include, url, patterns
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.views.generic.base import TemplateView

urlpatterns = [
    url(r'^get_group/(?P<group_key>\w+)/$', views.get_group, name='get_group'),
    url(r'^get_finished_meetings/(?P<group_key>\w+)/$', views.get_finished_meetings, name='get_finished_meetings'),
    url(r'^log_data/$', views.log_data, name='log_data'),

    url(r'^get_meeting/(?P<uuid>\w+)/$', views.get_meeting, name='get_meeting'),
    url(r'^get_meetings/$', views.get_meetings, name='get_meetings'),
    url(r'^get_groups/$', views.get_groups, name='get_groups'),
    url(r'^get_meeting_date/$', views.get_meeting_date, name='get_meeting_date'),
    url(r'^report/(?P<group_name>\w+)/$', views.report, name='report'),
    url(r'^data_process/$', views.data_process, name='data_process'),
]
urlpatterns += static( settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
