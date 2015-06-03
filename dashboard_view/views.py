# -*- coding: utf-8 -*-
import json
from datatableview.utils import split_real_fields, filter_real_fields, get_first_orm_bit, get_field_definition, \
    resolve_orm_path, FIELD_TYPES, ObjectListResult
from datatableview.views import DatatableMixin, log
import dateutil
from django import forms
from django.contrib import auth, messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import logout
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models.fields import Field, FieldDoesNotExist
from django.db.models.query_utils import Q
from django.forms.widgets import Media, PasswordInput
from django.template.base import TemplateDoesNotExist
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.utils.text import smart_split
from django.utils.translation import ugettext as _, pgettext
from django.views.generic.base import ContextMixin, TemplateView, RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, FormView, CreateView
from django.views.generic.list import ListView
import operator
import six
from dashboard_view.listview_actions import DashboardListViewActions
from dashboard_view.listview_filters import DashboardListViewFilters


class DashboardMenu():
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

        if hasattr(self, 'fields') and self.fields is not None:
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

        if hasattr(self, 'filters') and self.filters:
            filters = DashboardListViewFilters(view=self, filters_list=self.filters)
            context['filters_html'] = filters.render_filters_html()
            context['filters_js'] = filters.render_filters_js()

        if hasattr(self, 'actions') and self.actions:
            actions = DashboardListViewActions(view=self, actions_list=self.actions)
            context['actions_menu'] = actions.render_group_selection_menu()
            context['actions_html'] = actions.render_actions_html()
            context['actions_js'] = actions.render_actions_js()

        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(DashboardView, self).dispatch(request, *args, **kwargs)


class DashboardListView(DatatableMixin, ListView, DashboardView):
    filters = None
    actions = [
        'remove'
    ]

    def get_datatable_options(self):
        if type(self.datatable_options) is not dict:
            self.datatable_options = {}
        self.datatable_options["structure_template"] = "datatableview/bootstrap_structure_condensed.html"

        if "columns" not in self.datatable_options:
            if self.fields:
                self.datatable_options["columns"] = self.fields

        return self.datatable_options

    def apply_queryset_options(self, queryset):
        """
        Interprets the datatable options.

        Options requiring manual massaging of the queryset are handled here.  The output of this
        method should be treated as a list, since complex options might convert it out of the
        original queryset form.

        """

        options = self._get_datatable_options()

        # These will hold residue queries that cannot be handled in at the database level.  Anything
        # in these variables by the end will be handled manually (read: less efficiently)
        sort_fields = []
        searches = []

        # This count is for the benefit of the frontend datatables.js
        total_initial_record_count = queryset.count()

        if options['ordering']:
            db_fields, sort_fields = split_real_fields(self.model, options['ordering'])
            queryset = queryset.order_by(*db_fields)

        if options['search']:
            db_fields, searches = filter_real_fields(self.model, options['columns'],
                                                     key=get_first_orm_bit)
            db_fields.extend(options['search_fields'])

            queries = []  # Queries generated to search all fields for all terms
            search_terms = map(lambda q: q.strip("'\" "), smart_split(options['search']))

            for term in search_terms:
                term_queries = []  # Queries generated to search all fields for this term
                # Every concrete database lookup string in 'columns' is followed to its trailing field descriptor.  For example, "subdivision__name" terminates in a CharField.  The field type determines how it is probed for search.
                for column in db_fields:
                    column = get_field_definition(column)
                    for component_name in column.fields:
                        field_queries = []  # Queries generated to search this database field for the search term

                        field = resolve_orm_path(self.model, component_name)
                        if isinstance(field, tuple(FIELD_TYPES['text'])):
                            field_queries = [{component_name + '__icontains': term}]
                        elif isinstance(field, tuple(FIELD_TYPES['date'])):
                            try:
                                date_obj = dateutil.parser.parse(term)
                            except ValueError:
                                # This exception is theoretical, but it doesn't seem to raise.
                                pass
                            except TypeError:
                                # Failed conversions can lead to the parser adding ints to None.
                                pass
                            else:
                                field_queries.append({component_name: date_obj})

                            # Add queries for more granular date field lookups
                            try:
                                numerical_value = int(term)
                            except ValueError:
                                pass
                            else:
                                if 0 < numerical_value < 3000:
                                    field_queries.append({component_name + '__year': numerical_value})
                                if 0 < numerical_value <= 12:
                                    field_queries.append({component_name + '__month': numerical_value})
                                if 0 < numerical_value <= 31:
                                    field_queries.append({component_name + '__day': numerical_value})
                        elif isinstance(field, tuple(FIELD_TYPES['boolean'])):
                            if term.lower() in ('true', 'yes'):
                                term = True
                            elif term.lower() in ('false', 'no'):
                                term = False
                            else:
                                continue

                            field_queries = [{component_name: term}]
                        elif isinstance(field, tuple(FIELD_TYPES['integer'])):
                            try:
                                field_queries = [{component_name: int(term)}]
                            except ValueError:
                                pass
                        elif isinstance(field, tuple(FIELD_TYPES['float'])):
                            try:
                                field_queries = [{component_name: float(term)}]
                            except ValueError:
                                pass
                        elif isinstance(field, tuple(FIELD_TYPES['ignored'])):
                            pass
                        else:
                            raise ValueError("Unhandled field type for %s (%r) in search." % (component_name, type(field)))

                        # print field_queries

                        # Append each field inspection for this term
                        term_queries.extend(map(lambda q: Q(**q), field_queries))
                # Append the logical OR of all field inspections for this term
                if len(term_queries):
                    queries.append(reduce(operator.or_, term_queries))
            # Apply the logical AND of all term inspections
            if len(queries):
                queryset = queryset.filter(reduce(operator.and_, queries))

        filters = DashboardListViewFilters(self.request.GET)
        queryset = filters.apply_filters(queryset)

        # TODO: Remove "and not searches" from this conditional, since manual searches won't be done
        if not sort_fields and not searches:
            # We can shortcut and speed up the process if all operations are database-backed.
            object_list = queryset
            if options['search']:
                object_list._dtv_unpaged_total = queryset.count()
            else:
                object_list._dtv_unpaged_total = total_initial_record_count
        else:
            object_list = ObjectListResult(queryset)

            # # Manual searches
            # # This is broken until it searches all items in object_list previous to the database
            # # sort. That represents a runtime load that hits every row in code, rather than in the
            # # database. If enabled, this would cripple performance on large datasets.
            # if options['i_walk_the_dangerous_line_between_genius_and_insanity']:
            #     length = len(object_list)
            #     for i, obj in enumerate(reversed(object_list)):
            #         keep = False
            #         for column_info in searches:
            #             column_index = options['columns'].index(column_info)
            #             rich_data, plain_data = self.get_column_data(column_index, column_info, obj)
            #             for term in search_terms:
            #                 if term.lower() in plain_data.lower():
            #                     keep = True
            #                     break
            #             if keep:
            #                 break
            #
            #         if not keep:
            #             removed = object_list.pop(length - 1 - i)
            #             # print column_info
            #             # print data
            #             # print '===='

            # Sort the results manually for whatever remaining sort options are left over
            def data_getter_orm(field_name):
                def key(obj):
                    try:
                        return reduce(getattr, [obj] + field_name.split('__'))
                    except (AttributeError, ObjectDoesNotExist):
                        return None
                return key

            def data_getter_custom(i):
                def key(obj):
                    rich_value, plain_value = self.get_column_data(i, options['columns'][i], obj)
                    return plain_value
                return key

            # Sort the list using the manual sort fields, back-to-front.  `sort` is a stable
            # operation, meaning that multiple passes can be made on the list using different
            # criteria.  The only catch is that the passes must be made in reverse order so that
            # the "first" sort field with the most priority ends up getting applied last.
            for sort_field in sort_fields[::-1]:
                if sort_field.startswith('-'):
                    reverse = True
                    sort_field = sort_field[1:]
                else:
                    reverse = False

                if sort_field.startswith('!'):
                    key_function = data_getter_custom
                    sort_field = int(sort_field[1:])
                else:
                    key_function = data_getter_orm

                try:
                    object_list.sort(key=key_function(sort_field), reverse=reverse)
                except TypeError as err:
                    log.error("Unable to sort on {0} - {1}".format(sort_field, err))

            object_list._dtv_unpaged_total = len(object_list)

        object_list._dtv_total_initial_record_count = total_initial_record_count
        return object_list



    def get_column_data(self, i, name, instance):
        """ Finds the backing method for column ``name`` and returns the generated data. """
        values = super(DashboardListView, self).get_column_data(i, name, instance)

        if hasattr(instance._meta.model, 'get_absolute_url'):
            values = (u'<a href="%s">%s</a>' % (instance.get_absolute_url(), values[0]), values[1])

        return values

    def post(self, request):
        actions = DashboardListViewActions(self.request, view=self)
        return actions.apply_action()



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


class LoginForm(forms.Form):
    username = forms.CharField(label=_("Username/Email"))
    password = forms.CharField(label=_("Password"), widget=PasswordInput)

class LoginView(FormView):
    form_class = LoginForm
    success_url = reverse_lazy('dashboard_overview')
    template_name = "login.html"

    def get_success_url(self):
        next = self.request.GET.get('next', False)
        if next:
            return next
        return super(LoginView, self).get_success_url()

    def form_valid(self, form):
        username = form.cleaned_data.get('username', '')
        password = form.cleaned_data.get('password', '')

        if '@' in username:
            user = User.objects.filter(email=username).first()
            if user is not None:
                username = user.username

        user = auth.authenticate(username=username, password=password)

        if user is None:
            raise ValidationError(_("Invalid username or password"), code='invalid_username_or_password')
        if not user.is_active:
            raise ValidationError(_("User is not active"), code='user_is_not_active')

        login(self.request, user)
        return super(LoginView, self).form_valid(form)

class LogoutView(RedirectView):
    url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        if not request.user.is_anonymous():
            logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)