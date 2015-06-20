from django.utils.safestring import mark_safe
from dashboard_view.views import DashboardView


class DashboardWidget:
    ajax_view = 'dashboard:widget_ajax_call'
    name = None
    report_view = None

    def render(self):
        raise NotImplementedError

    def run_action(self):
        raise NotImplementedError

    @staticmethod
    def render_widgets(widgets_list):
        html_output = u''
        js_output = u''
        for widget in widgets_list:
            rendered_widget = widget.render()
            html_output += rendered_widget[0]
            js_output += rendered_widget[1]

        return (mark_safe(html_output), mark_safe(js_output))

