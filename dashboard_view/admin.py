from django.contrib import admin

# Register your models here.
from django.contrib.admin.sites import AdminSite
from django.utils.translation import gettext as _
from dashboard_view.dashboard_widgets import DashboardWidget
from dashboard_view.views import DashboardProfileView, DashboardFormView


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
        if self.widgets:
            rendered_widgets = DashboardWidget.render_widgets(self.widgets)
            context['dashboard_widgets_html'] = rendered_widgets[0]
            context['dashboard_widgets_js'] = rendered_widgets[1]
        return context

    def register_report(self, report_class):
        if not self.reports:
            self.reports = []
        report = report_class(admin_site=self)
        self.reports.append(report)
        self.menu.add(report)

    def register_widget(self, widget_class):
        if not self.widgets:
            self.widgets = []
        widget = widget_class()
        self.widgets.append(widget)

    def get_widget_ajax_call(self, request):
        if request.GET:
            try:
                widget_name = request.GET.get('widget_name', '')
                for w in self.widgets:
                    if w.name == widget_name:
                        widget = w
                if callable(getattr(widget, 'run_action', None)):
                    return getattr(widget, 'run_action')(request)
            except AttributeError:
                return (u'', u'', )

    def get_urls(self):
        from django.conf.urls import url

        urlpatterns = super(DashboardAdminSite, self).get_urls()

        #report urls
        if self.reports:
            for r in self.reports:
                urlpatterns += [
                    url(r'^reports/%s/$' % r.name, view=r.get_view(), name='report_' + r.name),
                ]

        #widget ajax call
        urlpatterns += [
            url(r'^widget_ajax$', self.get_widget_ajax_call, name="widget_ajax_call"),
        ]

        return urlpatterns