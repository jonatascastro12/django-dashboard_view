import locale
from django.utils.safestring import mark_safe


def format_currency(value, with_icon=True, zero=None, html_formated=True):
    locale.setlocale(locale.LC_MONETARY, '')
    icon = ''

    if not html_formated:
        return locale.currency(value, grouping=True)

    if value is None:
        return mark_safe("<span class=\"%s\">%s</span> %s" % ('text-success',  locale.currency(0), icon))
    if value > 0:
        class_type = 'text-success'
        if with_icon:
            icon = '<span class="text-success fa fa-plus"></span>'
    elif value == 0 and zero is not None:
        return zero
    else:
        value *= -1
        class_type = 'text-danger'
        if with_icon:
            icon = '<span class="text-danger fa fa-minus"></span>'

    return mark_safe("<span class=\"%s\">%s</span> %s" % (class_type,  locale.currency(value, grouping=True), icon))


class NoDefaultProvided(object):
    pass

def getattrd(obj, name, default=NoDefaultProvided):
    """
    Same as getattr(), but allows dot notation lookup
    Discussed in:
    http://stackoverflow.com/questions/11975781
    """

    try:
        if '__' in name:
            return reduce(getattr, name.split("__"), obj)
        else:
            return reduce(getattr, name.split("."), obj)
    except AttributeError, e:
        if default != NoDefaultProvided:
            return default
        raise