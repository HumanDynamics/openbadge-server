from django.conf.urls import include, url, patterns
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.views.generic.base import TemplateView

urlpatterns = [
    url(r'^log_data/$', views.log_data, name='log_data'),

    url(r'^report/(?P<group_name>\w+)/$', views.report, name='report'),

]
urlpatterns += static( settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
