from django.conf.urls import patterns, url
from dashboard_view import dashboard_site
from dashboard_view.dashboard_widgets import DashboardWidget

urlpatterns = patterns('',
    url(r'^widget_ajax$', DashboardWidget.ajax_call, name="widget_ajax_call"),
)


