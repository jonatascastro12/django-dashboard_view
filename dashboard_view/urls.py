from django.conf.urls import patterns, url, include
from dashboard_view.views import DashboardOverviewView, DashboardProfileView

urlpatterns = patterns('',
    url(r'^$', DashboardOverviewView.as_view(), name="dashboard_overview"),
    url(r'^/profile$', DashboardProfileView.as_view(), name="dashboard_overview"),
)
