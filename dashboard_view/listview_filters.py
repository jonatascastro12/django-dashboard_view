import json
import operator
from django.db.models.query_utils import Q
from django.template.context import Context
from django.template.loader import get_template
from django.utils.safestring import mark_safe
import six


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
            choices = self.view.model._meta.get_field_by_name(field_name)[0].choices

        c = Context({
            'field_name': field_name,
            'filter_label': filter_label,
            'datatable_class': datatable_class,
            'choices': choices
        })
        template_js = get_template('filters/checkbox_choice_js.html')

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