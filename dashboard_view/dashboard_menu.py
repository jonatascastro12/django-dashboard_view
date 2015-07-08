from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from dashboard_view.dashboard_reports import DashboardReport


class DashboardMenu():
    menu = []

    def __init__(self, menu=None):
        self.menu = menu

    def add(self, item):
        if isinstance(item, DashboardReport):
            found_report = False
            for obj in self.menu:
                if obj['name'] == 'reports':
                    found_report = True
                    obj['children'].append(
                        {'name': item.name, 'verbose_name': item.verbose_name,
                        'link': reverse_lazy('dashboard:report_'+item.name), 'icon_class': item.icon, }
                    )
            if not found_report:
                self.menu.append({'name': 'reports', 'icon_class': 'fa-file-text', 'verbose_name': _('Reports'), 'children':
                    [{'name': item.name, 'verbose_name': item.verbose_name,
                        'link': reverse_lazy('dashboard:report_'+item.name), 'icon_class': item.icon, },
                    ]})

    def render(self, request=None, permission=None):
        output = u''

        user = request.user

        for item in self.menu:

            if item.get('perm', False) and not user.has_perm(item.get('perm', '')):
                continue

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

                    if child_item.get('perm', False) and not user.has_perm(child_item.get('perm', '')):
                        continue

                    link = child_item.get('link', '#')
                    try:
                        active = 'active' if link == request.path_info else ''
                    except TypeError:
                        active = 'active' if link._proxy____args[0] == request.resolver_match.view_name else ''

                    icon_class = child_item.get('icon_class', '')
                    verbose_name = child_item.get('verbose_name', child_item['name'])
                    arrow = '<span class="fa arrow"></span>' if 'children' in child_item else ''
                    output += u'<li><a href="{0}" class="{1}"><i class="fa {2} ' \
                              u'fa-fw"></i>{3} {4}</a>'.format(link, '', icon_class, verbose_name, arrow)
                    if 'children' in child_item:
                        output += u'<ul class="nav nav-third-level">'  # .format(' open' if active != '' else '')
                        for third_level in child_item['children']:
                            if third_level.get('perm', False) and not user.has_perm(third_level.get('perm', '')):
                                continue

                            link = third_level.get('link', '#')
                            try:
                                active = 'active' if link == request.path_info else ''
                            except TypeError:
                                active = 'active' if link._proxy____args[0] == request.resolver_match.view_name else ''
                            icon_class = third_level.get('icon_class', '')
                            verbose_name = third_level.get('verbose_name', third_level['name'])
                            output += u'<li><a href="{0}" class="{1}"><i class="fa {2} ' \
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
