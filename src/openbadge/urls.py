from django.conf.urls import include, url
from . import views
from django.views.generic.base import TemplateView

urlpatterns = [
    url(r'^get_group/(?P<group_key>\w+)/$', views.get_group, name='get_group'),

    url(r'^log_data/$', views.log_data, name='log_data'),
]

