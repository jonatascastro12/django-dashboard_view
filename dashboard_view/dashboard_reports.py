from django.core.urlresolvers import reverse_lazy
from django.http.response import HttpResponseRedirect
from django.utils.text import slugify, camel_case_to_spaces
from dashboard_view.views import DashboardFormView

class DashboardReportView(DashboardFormView):
    template_name = "generics/dashboard_report.html"
    report = None
    admin_site = None
    model = None

    def __init__(self, report, admin_site, **kwargs):
        super(DashboardReportView, self).__init__(**kwargs)
        self.report = report
        self.admin_site = admin_site
        self.form_class = self.report.filter_form
        self.model = self.report.model

    def get_success_url(self):
        return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        return self.render_to_response(context=self.get_context_data(form=form, objects=self.report.get_queryset()))

class DashboardReport:
    queryset = None
    model = None
    form_class = None
    verbose_name = None
    name = None
    icon = None

    def __init__(self, admin_site):
        self.admin_site = admin_site

        if not self.verbose_name:
            self.verbose_name = camel_case_to_spaces(self.__class__.__name__.replace('Report', '')).title()
        self.name = self.get_slug()

    def get_queryset(self):
        return self.queryset

    def get_context(self, form, objects, context):
        context['form'] = form
        context['objects'] = objects

        return context

    def get_slug(self):
        if self.verbose_name:
            return slugify(self.verbose_name).replace('-', '_')
        else:
            return slugify(self.__class__.__name__).replace('-', '_')

    def get_absolute_url(self):
        return reverse_lazy('report_'+self.name)

    def get_view(self):
        view = DashboardReportView.as_view(report=self, admin_site=self.admin_site)
        return view


