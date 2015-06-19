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