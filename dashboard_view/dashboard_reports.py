from django.http.response import HttpResponseRedirect
from django.utils.text import slugify
from dashboard_view.views import DashboardFormView


class DashboardReport():
    queryset = None
    model = None
    form_class = None
    verbose_name = None

    @staticmethod
    def register(dashboard, class_obj):
        dashboard.reports.append(class_obj)

    def get_queryset(self):
        return self.queryset

    def get_context(self, form, objects, context):
        context['form'] = form
        context['objects'] = objects

        return context

    def get_slug(self):
        if self.verbose_name:
            return slugify(self.verbose_name)
        else:
            return self.__class__.__name__
    
    def urls(self):
        from django.conf.urls import url
        urlpatterns = [
            url('', self.get_view(), 'report_%s' % self.get_slug())
        ]

        return urlpatterns

    def get_view(self):
        view = DashboardReportView(report=self)
        return view.as_view()

class DashboardReportView(DashboardFormView):
    template_name = "generics/dashboard_report.html"
    report = None

    def __init__(self, report):
        super(DashboardReportView, self).__init__()
        self.report = report
        self.form = report.filter_form

    def get_success_url(self):
        return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        return self.render_to_response(context=self.get_context_data(form=form, objects=self.get_queryset()))
