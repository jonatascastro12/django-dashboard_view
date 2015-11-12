from django.utils.safestring import mark_safe
from dashboard_view.views import DashboardView


class DashboardWidget:
    ajax_view = 'dashboard:widget_ajax_call'
    name = None
    report_view = None
    perm = None
    verbose_name = None
    color_css_class = None
    grid_css_class = None

    def render(self):
        raise NotImplementedError

    def run_action(self):
        raise NotImplementedError

    @staticmethod
    def render_widgets(widgets_list, request):
        html_output = u''
        js_output = u''

        user = request.user
        for widget in widgets_list:
            if (widget.perm is not None and not user.has_perm(widget.perm)):
                continue

            color_css_class = widget.color_css_class
            grid_css_class = widget.grid_css_class
            if color_css_class is None:
                color_css_class = 'primary'
            if grid_css_class is None:
                grid_css_class = 'col-xs-12 col-lg-3'

            rendered_widget = widget.render()
            html_output += '<div class="{1}"><li class="panel panel-{0} {2}">'.format(color_css_class, grid_css_class, widget.name + '_widget')+rendered_widget[0]+'</li></div>'
            js_output += rendered_widget[1]

        return (mark_safe(html_output), mark_safe(js_output))

