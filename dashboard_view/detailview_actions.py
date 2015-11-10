import json
import operator
from django.contrib import messages
from django.db.models.query_utils import Q
from django.http.response import HttpResponse
from django.template.context import Context
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

import six

class DetailViewAction:
    name = None
    report_view = None
    perm = None

    def __init__(self, request=None, actions_list=None, view=None):
        if request:
            self.request = request
            self.action = self.post_action(request.body)
        if actions_list:
            self.actions_list = self.complete_action_list(actions_list)
        if view:
            self.view = view

    def render(self):
        raise NotImplementedError

    def run_action(self):
        raise NotImplementedError

    @staticmethod
    def render_detail_view_action(detail_view_action_list, view):
        html_output = u''
        js_output = u''

        permitted_list = []

        user = view.request.user
        for action in detail_view_action_list:
            model_app = view.model._meta.app_label
            model_name = view.model._meta.model_name
            if (action.perm is not None and not user.has_perm((action.perm  % (model_app, model_name, )) if '%' in action.perm else action.perm)):
                continue
            permitted_list.append(action)
            action_intance = action(view=view)
            rendered = action_intance.render()
            html_output += rendered[0]
            js_output += rendered[1]

        c = Context({
            'actions': permitted_list
        })

        t = get_template('detailview_actions/_group_selection_menu.html')
        menu_output = t.render(c)

        return (mark_safe(menu_output), mark_safe(html_output), mark_safe(js_output))




class EditDetailViewAction(DetailViewAction):
    name = 'edit'
    perm = '%s.change_%s'
    color_class = 'default'
    icon_class = 'pencil'
    label = _('Edit')


    def render(self):
        c = Context({
            'edit_view': self.view.request.resolver_match.view_name.replace('_detail', '_edit'),
            'obj_id': self.view.object.id
        })
        template_js = get_template('detailview_actions/edit_js.html')
        return ('', template_js.render(c), )

class RemoveDetailViewAction(DetailViewAction):
    name = 'remove'
    perm = '%s.delete_%s'
    color_class = 'danger'
    icon_class = 'eraser'
    label = _('Remove')

    def render(self):
        c = Context({
            'action_name': self.name,
            'ajax_view': self.view.request.resolver_match.view_name,
            'list_view': self.view.request.resolver_match.view_name.replace('_detail', ''),
            'obj_id': self.view.object.id
        })

        template_html = get_template('detailview_actions/remove.html')
        template_js = get_template('detailview_actions/remove_js.html')

        return (template_html.render(c), template_js.render(c))

    def run_action(self, data):
        if data is not None:
            try:
                selected_object = self.view.model._default_manager.filter(id=data).all()
                selected_object.delete()
                messages.success(self.view.request, _('Deleted successfully!'))
                return HttpResponse(status=200)
            except:
                raise
                return HttpResponse(status=401)
