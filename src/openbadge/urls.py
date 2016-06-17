from django.conf.urls import include, url, patterns
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.views.generic.base import TemplateView

urlpatterns = [
    url(r'^log_data/$', views.log_data, name='log_data'),

    url(r'^weekly_group_report/(?P<group_key>\w+)/(?P<week_num>[0-9]+)$', views.weekly_group_report, name='weekly_group_report'),

]
urlpatterns += static( settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
