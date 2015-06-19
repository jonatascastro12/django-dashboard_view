from django.contrib import admin

# Register your models here.
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import AdminSite
from django.utils.translation import gettext as _
from dashboard_view.dashboard_menu import DashboardMenu
from dashboard_view.views import DashboardListView


class DashboardAdminSite(AdminSite):
    index_template = "dashboard_base.html"
    login_template = "login.html"
    index_title = _('Overview')

    menu = None
    reports = None
    widgets = None

    def each_context(self, request):
        context = super(DashboardAdminSite, self).each_context(request)
        if self.menu:
            context['dashboard_menu'] = self.menu.render(request)

        return context

    def register_report(self, report_class):
        if not self.reports:
            self.reports = []
        report = report_class(admin_site=self)
        self.reports.append(report)
        self.menu.add(report)

    def get_urls(self):
        from django.conf.urls import url

        urlpatterns = super(DashboardAdminSite, self).get_urls()

        #report urls
        if self.reports:
            for r in self.reports:
                urlpatterns += [
                    url(r'^reports/%s/$' % r.name, view=r.get_view(), name='report_' + r.name),
                ]

        return urlpatterns