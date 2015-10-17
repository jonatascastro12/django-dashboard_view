import hashlib
import json
import operator
from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields.related import ForeignKey
from django.db.models.query_utils import Q
from django.forms.forms import Form
from django.template.context import Context
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django_select2.fields import AutoModelSelect2Field, AutoModelSelect2MultipleField
import six
from django_select2_extension.widgets import NewAutoHeavySelect2MultipleWidget


class DashboardListViewFilters:
    filters = None
    filters_list = None
    view = None

    def __init__(self, get_request=None, filters_list=None, view=None):
        if get_request:
            self.filters = self.get_filters(get_request)
        if filters_list:
            self.filters_list = filters_list
        if view:
            self.view = view

    def get_filters(self, get):
        f = []
        for k, v in get.iteritems():
            if k.startswith('filter-'):
                fk = k.split('-')
                f.append({'n': fk[1], 'field': fk[2], 'filter': fk[3], 'data': json.loads(v)})
        return f

    def filter_date_range(self, f, term_queries):
        if f['data']['date_range_A'] != u'' or f['data']['date_range_B'] != u'':
            if f['data']['date_range_A'] == u'':
                term_queries.append(Q(**{f['field'] + '__lte': f['data']['date_range_B']}))
            elif f['data']['date_range_B'] == u'':
                term_queries.append(Q(**{f['field'] + '__gte': f['data']['date_range_A']}))
            else:
                term_queries.append(Q(**{f['field'] + '__range': (f['data']['date_range_A'], f['data']['date_range_B'])}))
        return term_queries

    def filter_input_text(self, f, term_queries):
        if f['data']['value'] != u'':
            term_queries.append(Q(**{f['field'] + '__icontains': f['data']['value']}))
        return term_queries

    def filter_checkbox_choice(self, f, term_queries):
        if len(f['data']['values']) > 0:
            field_queries = []
            for val in f['data']['values']:
                field_queries.append(Q(**{f['field']: val}))
            term_queries.append(reduce(operator.or_, field_queries))
        return term_queries

    def filter_select2_multichoice(self, f, term_queries):
        if f['data'].get('value'):
            field_queries = []
            for val in f['data']['value'].split(u'\x1f'):
                field_queries.append(Q(**{f['field']: val}))
            term_queries.append(reduce(operator.or_, field_queries))
        return term_queries

    def render_filter(self, f):
        field_name = ''
        filter_label = ''
        filter_type = ''
        choices = None
        if type(f) is tuple:
            filter_label = f[0]
            field_name = f[1]

            if len(f) > 3:
                choices = f[3]
            elif len(f) > 2:
                filter_type = f[2]
            else:
                if (self.view.model._meta.get_field_by_name(field_name)[0].choices is not None):
                    filter_type = 'checkbox_choice'
                else:
                    filter_type = 'input_text'

        elif f is not None and f != '' and isinstance(f, six.string_types):
            field_name = f
            filter_label = f.title()
            if (self.view.model._meta.get_field_by_name(field_name)[0].choices is not None):
                filter_type = 'checkbox_choice'
            else:
                filter_type = 'input_text'

        try:
            if callable(getattr(self, '_render_filter_%s' % filter_type, None)):
                return getattr(self, '_render_filter_%s' % filter_type)(filter_label, field_name, choices)
        except AttributeError:
            return (u'', u'', )

        return ('', '', )

    def _render_filter_date_range(self, filter_label, field_name, choices=None, datatable_class='datatable'):
        template_html = get_template('filters/date_range.html')
        c = Context({
            'field_name': field_name,
            'filter_label': filter_label,
            'datatable_class': datatable_class
        })
        template_js = get_template('filters/date_range_js.html')

        return (template_html.render(c), template_js.render(c), )

    def _render_filter_input_text(self, filter_label, field_name, choices=None, datatable_class='datatable'):
        template_html = get_template('filters/input_text.html')
        c = Context({
            'field_name': field_name,
            'filter_label': filter_label,
            'datatable_class': datatable_class
        })
        template_js = get_template('filters/input_text_js.html')

        return (template_html.render(c), template_js.render(c), )

    def _render_filter_checkbox_choice(self, filter_label, field_name, datatable_class='datatable', choices=None):
        template_html = get_template('filters/checkbox_choice.html')

        if choices is None:
            try:
                field = self.view.model._meta.get_field_by_name(field_name)
            except FieldDoesNotExist:
                if '__' in field_name:
                    real_field_name = field_name.split('__')[0]
                    choiced_attr_name = field_name.split('__')[1]
                    fields = self.view.model._meta.get_field_by_name(real_field_name)
                    choices = fields[0].rel.to._meta.get_field(choiced_attr_name).choices

            if choices is None:
                if isinstance(field[0], ForeignKey):
                    try:
                        related_objs = field[0].related.model.objects.all()
                    except AttributeError:
                        related_objs = field[0].related.model.accounted.all()
                    choices = []
                    for obj in related_objs:
                        choices.append((obj.id, obj.__unicode__()))
                else:
                    choices = field[0].choices

        c = Context({
            'field_name': field_name,
            'filter_label': filter_label,
            'datatable_class': datatable_class,
            'choices': choices
        })
        template_js = get_template('filters/checkbox_choice_js.html')

        return (template_html.render(c), template_js.render(c), )

    def _render_filter_select2_multichoice(self, filter_label, field_name, datatable_class='datatable', choices=None):
        template_html = get_template('filters/select2_multichoice.html')

        if choices is None:
            field = self.view.model._meta.get_field_by_name(field_name)
            if isinstance(field[0], ForeignKey):
                try:
                    related_objs = field[0].related.model.objects
                except AttributeError:
                    related_objs = field[0].related.model.accounted

        class Select2Field(AutoModelSelect2MultipleField):
            queryset = related_objs
            search_fields = ['title__icontains']
            widget = NewAutoHeavySelect2MultipleWidget


        class Select2Form(Form):
            def __init__(self, *args, **kwargs):
                super(Select2Form, self).__init__(*args, **kwargs)
                self.fields['filter_select2_multichoice_' + field_name] = Select2Field(auto_id=field_name)


        c = Context({
            'field_name': field_name,
            'filter_label': filter_label,
            'form': Select2Form(),
            'datatable_class': datatable_class,
            'choices': choices
        })
        template_js = get_template('filters/select2_multichoice_js.html')

        return (template_html.render(c), template_js.render(c), )

    def render_filters_html(self):
        output = u''
        for f in self.filters_list:
            output += u'<li class="list-group-item">%s</li>' % self.render_filter(f)[0]
        output = u'<ul id="collapseOne" class="list-group filter-collapse collapse">%s</ul>' % output
        return mark_safe(output)

    def render_filters_js(self):
        output = u''
        for f in self.filters_list:
            output += self.render_filter(f)[1]
        return mark_safe(output)

    def apply_filters(self, queryset):
        term_queries = []
        for f in self.filters:
            if callable(getattr(self, 'filter_'+f['filter'], None)):
                term_queries = getattr(self, 'filter_'+f['filter'])(f, term_queries)

        # Apply the logical AND of all term inspections
        if len(term_queries):
            queryset = queryset.filter(reduce(operator.and_, term_queries))
        return queryset