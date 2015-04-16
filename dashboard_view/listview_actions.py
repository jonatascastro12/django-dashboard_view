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


class DashboardListViewActions:
    actions = None
    actions_list = None
    view = None
    request = None

    def __init__(self, request=None, actions_list=None, view=None):
        if request:
            self.request = request
            self.action = self.post_action(request.body)
        if actions_list:
            self.actions_list = self.complete_action_list(actions_list)
        if view:
            self.view = view

    def post_action(self, post):
        obj = json.loads(post)
        return {'execute': '_action_' + obj['action'], 'data': obj['data']}

    def complete_action_list(self, list):
        i = 0
        for a in list:
            if isinstance(a, six.string_types) and a == 'remove':
                list[i] = {'name': 'remove', 'label': _('Remove'), 'icon_class': 'remove'}
            elif isinstance(a, six.string_types):
                list[i] = {'name': a, 'label': a, 'icon_class': 'ok'}
            i += 1
        return list

    def render_action(self, a):
        action_type = a.get('name', '')
        try:
            if callable(getattr(self, '_render_action_%s' % action_type, None)):
                return getattr(self, '_render_action_%s' % action_type)()
        except AttributeError:
            return (u'', u'', )

        return ('', '', )

    def _render_action_remove(self):
        template_html = get_template('actions/remove.html')
        template_menu_item = '<li><a id="remove" href="">' + \
               '<span class="glyphicon glyphicon-remove" aria-hidden="true"></span>' + \
                _('Remove') + \
               '</a></li>'
        c = Context({
            'list_view': self.view.request.resolver_match.view_name,
            'model_verbose_name': '',
            'model_verbose_name_plural': '',
        })
        template_js = get_template('actions/remove_js.html')

        return (template_html.render(c), template_js.render(c), template_menu_item)


    def render_actions_html(self):
        output = u''
        for f in self.actions_list:
            output += self.render_action(f)[0]
        return mark_safe(output)

    def render_group_selection_menu(self):
        template = get_template('actions/_group_selection_menu.html')
        c = Context({
            'actions': self.actions_list
        })
        return template.render(c)

    def render_actions_js(self):
        output = u''
        for f in self.actions_list:
            output += self.render_action(f)[1]
        return mark_safe(output)

    def _action_remove(self, data):
        if data is not None:
            ids = data.get('ids', None)
            try:
                selected_objects = self.view.model.objects.filter(id__in=ids).all()
                selected_objects.delete()
                messages.success(self.request, _('Deleted successfully!'))
                return HttpResponse(status=200)
            except:
                raise
                return HttpResponse(status=401)

    def apply_action(self):
        try:
            if callable(getattr(self, self.action['execute'], None)):
                return getattr(self, self.action['execute'])(self.action['data'])
        except AttributeError:
            return HttpResponse(status=400)
