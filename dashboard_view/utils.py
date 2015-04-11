import locale
from django.utils.safestring import mark_safe


def format_currency(value):
    locale.setlocale(locale.LC_MONETARY, '')
    if value >= 0:
        class_type = 'text-success'
        icon = '<span class="text-success fa fa-plus"></span>'
    else:
        value *= -1
        class_type = 'text-danger'
        icon = '<span class="text-danger fa fa-minus"></span>'

    return mark_safe("<span class=\"%s\">%s</span> %s" % (class_type,  locale.currency(value), icon))