from django.conf.urls import include, url
from . import views
from django.views.generic.base import TemplateView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^get_group/(?P<group_key>\w+)/$', views.get_group, name='get_group'),
    url(r'^get_finished_meetings/(?P<group_key>\w+)/$', views.get_finished_meetings, name='get_finished_meetings'),

    url(r'^log_data/$', views.log_data, name='log_data'),
    
    url(r'^internal_report/$', views.internal_report, name='internal_report'),    
]

