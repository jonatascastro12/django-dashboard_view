# -*- coding: utf-8 -*-
import imghdr
import json
import os
from PIL import Image
from datatableview.views import DatatableMixin
from django.apps import apps
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models.base import Model
from django.db.models.fields import Field, FieldDoesNotExist
from django.forms.widgets import Media
from django.http.response import HttpResponse
from django.template.base import TemplateDoesNotExist
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _, pgettext
from django.views.generic.base import ContextMixin, View, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, FormView, CreateView, DeleteView
from django.views.generic.list import ListView
import six
from siscontrole.settings import INSTALLED_APPS


class DashboardMenu():
    app_list = [apps.get_app_config(app) for app in INSTALLED_APPS if
                not ("django" in app) and not ("nested" in app) and not ("bootstrap" in app) and not ("sorl" in app)]
    menu = []

    def __init__(self, menu):
        self.menu = menu

    def render(self, request=None, permission=None):
        output = u''
        for item in self.menu:
            link = item.get('link', '#')
            try:
                active = 'active' if link == request.path_info else ''
            except TypeError:
                active = 'active' if link._proxy____args[0] == request.resolver_match.view_name else ''
            icon_class = item.get('icon_class', '')
            verbose_name = item.get('verbose_name', item['name'])
            arrow = '<span class="fa arrow"></span>' if 'children' in item else ''
            output += u'<li><a href="{0}" class="{1}"><i class="fa {2} ' \
                      u'fa-fw"></i>{3} {4}</a>'.format(link, '', icon_class, verbose_name, arrow)
            if 'children' in item:
                item['children'].sort()
                output += u'<ul class="nav nav-second-level">'  # .format(' open' if active != '' else '')
                for child_item in item['children']:
                    link = child_item.get('link', '#')
                    try:
                        active = 'active' if link == request.path_info else ''
                    except TypeError:
                        active = 'active' if link._proxy____args[0] == request.resolver_match.view_name else ''

                    icon_class = child_item.get('icon_class', '')
                    verbose_name = child_item.get('verbose_name', child_item['name'])
                    arrow = '<span class="fa arrow"></span>' if 'children' in child_item else ''
                    output += u'<li><a href="{0}" class="{1}"><i class="fa {2}' \
                              u'fa-fw"></i>{3} {4}</a>'.format(link, '', icon_class, verbose_name, arrow)
                    if 'children' in child_item:
                        output += u'<ul class="nav nav-third-level">'  # .format(' open' if active != '' else '')
                        for third_level in child_item['children']:
                            link = third_level.get('link', '#')
                            try:
                                active = 'active' if link == request.path_info else ''
                            except TypeError:
                                active = 'active' if link._proxy____args[0] == request.resolver_match.view_name else ''
                            icon_class = third_level.get('icon_class', '')
                            verbose_name = third_level.get('verbose_name', third_level['name'])
                            output += u'<li><a href="{0}" class="{1}"><i class="fa {2}' \
                                      u'fa-fw"></i>{3}</a></li>'.format(link, '', icon_class, verbose_name)
                        output += u'</ul>'
                    output += u'</li>'
                output += u'</ul>'
            output += u'</li>'
        return output

    def menu_list(self):
        mlist = []
        ''' mlist.append({'link': '/dashboard', 'app_verbose_name': _('Overview')})
        for app in self.app_list:
            models = get_models(get_app(app.label))
            app_obj = {'app': app, 'app_verbose_name': app.verbose_name,
                       'models': [{'verbose_name': m._meta.verbose_name_plural,
                        'link': m._meta.model_name } for m in models if m._meta.model_name in ['member', 'church']]}
            mlist.append(app_obj)
        '''
        return mlist

class DashboardView(ContextMixin):
    menu = []

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        context['dashboard_menu'] = self.menu.render(self.request)
        context['app_list'] = self.menu.menu_list()
        context['media_css'] = Media()
        context['media_js'] = Media()

        if not hasattr(self, 'model'):
            return context

        try:
            get_template(
                self.model._meta.app_label + '/' + self.model._meta.model_name + self.template_name_suffix + '.html')
        except TemplateDoesNotExist:
            self.template_name = 'generics/dashboard' + self.template_name_suffix + '.html'


        context['list_view'] = self.request.resolver_match.view_name. \
            replace('_edit', '').replace('_add', '').replace('_detail', '')
        context['add_view'] = self.request.resolver_match.view_name. \
                                  replace('_edit', '').replace('_add', '').replace('_detail', '') + '_add'
        context['detail_view'] = self.request.resolver_match.view_name. \
                                     replace('_edit', '').replace('_add', '').replace('_detail', '') + '_detail'
        context['edit_view'] = self.request.resolver_match.view_name. \
                                   replace('_edit', '').replace('_add', '').replace('_detail', '') + '_edit'

        new_title = (pgettext('female', 'New') if hasattr(self.model._meta,
                                                          'gender') and self.model._meta.gender == 'F' else \
                         pgettext('male', 'New')) + u' ' + self.model._meta.verbose_name

        if self.template_name_suffix == '_form' and self.object:
            context[
                'page_name'] = self.model._meta.verbose_name + u' <small>' + self.object.__unicode__() + \
                               u' <span class="label label-warning">' + _('Editing') + u'</span></small> '
        elif self.template_name_suffix == '_detail':
            context['page_name'] = self.model._meta.verbose_name + u' <small>' + self.object.__unicode__() + \
                                   u'</small><a href="' + reverse(context['edit_view'], None, (),
                                                                  {'pk': self.object.pk}) + \
                                   u'" class="btn pull-right btn-primary">' + \
                                   _('Editar') + u'</a>'
        elif self.template_name_suffix == '_form':
            context['page_name'] = new_title
        else:
            context['page_name'] = self.model._meta.verbose_name_plural + \
                                   u'<a href="' + reverse(context['add_view']) + \
                                   u'" class="btn pull-right btn-success">' + \
                                   new_title + u'</a>'

        fields = list(self.model._meta.fields)
        context['fields'] = []

        if hasattr(self, 'datatable_options'):
            if self.datatable_options is not None:
                self.fields = self.datatable_options['columns']

        if self.fields:
            '''for f in fields:
                if f.name in self.fields:
                    context['fields'].append(f)'''

            for f in self.fields:
                if type(f) is not tuple and isinstance(f, six.string_types):
                    try:
                        context['fields'].append(self.model._meta.get_field_by_name(f)[0])
                    except FieldDoesNotExist:
                        if hasattr(self.model, f):
                            context['fields'].append(Field(verbose_name=f.title(), name=f))
                else:
                    try:
                        field = self.model._meta.get_field_by_name(f[1])[0]
                        field.verbose_name = f[0]
                        context['fields'].append(field)
                    except FieldDoesNotExist:
                        if hasattr(self.model, f[1]):
                            context['fields'].append(Field(verbose_name=f[0].title(), name=f[1]))

        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(DashboardView, self).dispatch(request, *args, **kwargs)


class DashboardListView(DatatableMixin, ListView, DashboardView):
    def get_datatable_options(self):
        if type(self.datatable_options) is not dict:
            self.datatable_options = {}
        self.datatable_options["structure_template"] = "datatableview/bootstrap_structure.html"
        return self.datatable_options

    def get_column_data(self, i, name, instance):
        """ Finds the backing method for column ``name`` and returns the generated data. """
        values = super(DashboardListView, self).get_column_data(i, name, instance)

        if hasattr(instance._meta.model, 'get_absolute_url'):
            values = (u'<a href="%s">%s</a>' % (instance.get_absolute_url(), values[0]), values[1])

        return values

    def delete(self, request):
        if (isinstance(request.body, six.string_types)):
            data = json.loads(request.body)
            ids = data.get('ids', None)
            try:
                selected_objects = self.model.objects.filter(id__in=ids).all()
                selected_objects.delete()
                messages.success(self.request, _('Deleted successfully!'))
                return HttpResponse(status=200)
            except:
                raise
                return HttpResponse(status=401)


class DashboardDetailView(DetailView, DashboardView):
    pass


class DashboardCreateView(CreateView, DashboardView):
    def form_valid(self, form):

        model_name = self.model._meta.verbose_name

        if self.object:
            object_name = ' ' + self.object.__unicode__() + ' '
        else:
            object_name = ' ' + form.instance.__unicode__() + ' '

        # LogEntry.objects.log_action(self.request.user.id, )
        messages.success(self.request, message=model_name + object_name + _('created successfully!'))
        return super(DashboardCreateView, self).form_valid(form)


class DashboardFormView(FormView, DashboardView):
    pass


class DashboardUpdateView(UpdateView, DashboardView):
    def form_valid(self, form):
        model_name = self.model._meta.verbose_name
        object_name = self.object.__unicode__()

        messages.success(self.request, message=model_name + ' ' + object_name + _(' updated successfully!'))
        return super(DashboardUpdateView, self).form_valid(form)


class DashboardOverviewView(TemplateView, DashboardView):
    template_name = "dashboard_base.html"

class DashboardProfileView(TemplateView, DashboardView):
    template_name = "dashboard_base.html"