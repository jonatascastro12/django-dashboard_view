from django.utils.safestring import mark_safe
from dashboard_view.views import DashboardView


class DashboardWidget():
    widgets_list = None

    def __init__(self, widgets_list=None):
        self.widgets_list = widgets_list

    def render_widget(self, widget):
        try:
            if callable(getattr(self, '_render_widget_%s' % widget, None)):
                return getattr(self, '_render_widget_%s' % widget)()
        except AttributeError:
            return (u'', u'', )

        return ('', '', )

    def render_widgets(self, request):
        html_output = u''
        js_output = u''
        for widget in self.widgets_list:
            html_output += self.render_widget(widget[0])[0]
            js_output += self.render_widget(widget[0])[1]

        return (mark_safe(html_output), mark_safe(js_output))

    @staticmethod
    def ajax_call(request):
        if request.GET:
            try:
                widget_name = request.GET.get('widget_name', '')
                widget = DashboardView.widget_class()
                if callable(getattr(widget, '_action_%s' % widget_name, None)):
                    return getattr(widget, '_action_%s' % widget_name)(request)
            except AttributeError:
                return (u'', u'', )