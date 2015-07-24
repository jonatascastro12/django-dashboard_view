from django import template
from django.forms.forms import BaseForm
from django.forms.formsets import BaseFormSet
from django.template import Context
from django.template.loader import get_template
from django.utils.translation import ugettext as _
import itertools
import six

register = template.Library()

@register.filter
def as_bootstrap(entity, layout="horizontal"):
    if issubclass(entity.__class__, BaseFormSet):
        template = get_template('bootstrap_form/formset.html')

        c = Context({
            'formset': entity
        })
    elif issubclass(entity.__class__, BaseForm):
        template = get_template('bootstrap_form/form.html')

        c = Context({
            'form': entity,
            'label_class': 'control-label',
        })
    else:
        if ',' in layout:
            args = layout.split(',')
        else:
            args = ('layout', None, None, )

        if len(args) == 2:
            args = (args[0], args[1], None, )

        if args[0] == 'inline':
            template = get_template('bootstrap_form/field_inline.html')
        else:
            template = get_template('bootstrap_form/field_horizontal.html')

        c = Context({
            'field': entity,
            'label_class': args[1],
            'field_container_class': args[2]
        })
    return template.render(c)

@register.simple_tag()
def field_as_bootstrap(form, field, layout="horizontal", label_class="", field_container_class=""):
    if layout == 'inline':
        template = get_template('bootstrap_form/field_inline.html')
    else:
        template = get_template('bootstrap_form/field_horizontal.html')

    c = Context({
        'form': form,
        'field': field,
        'label_class': label_class,
        'field_container_class': field_container_class
    })
    return template.render(c)

@register.simple_tag()
def buttons(submit_label=_('Save'), cancel_label=_('Cancel'), class_name='col-sm-offset-3 col-lg-offset-2 col-sm-8 col-lg-4'):

    template = get_template('bootstrap_form/buttons.html')

    c = Context({
        'submit_label': submit_label,
        'cancel_label': cancel_label,
        'class_name': class_name,
    })

    return template.render(c)

@register.filter
def add_class(field, class_name):
    if not isinstance(field, six.string_types):
        return field.as_widget(attrs={
            "class": " ".join((field.css_classes(), class_name))
        })


@register.filter
def add_areatext_attrs(field, attrs):
    if not isinstance(field, six.string_types):
        return field.as_widget(attrs={
            "rows": attrs.split(" ")[0],
            "cols": attrs.split(" ")[1],

        })

@register.filter
def add_placeholder(field, placeholder):
    return field.as_widget(attrs={
        "placeholder": " ".join((field.placeholders(), placeholder))
    })

@register.filter
def klass(ob):
    return ob.__class__.__name__.lower()


@register.filter
def chunks(value, chunk_length):
    """
    Breaks a list up into a list of lists of size <chunk_length>
    """
    clen = int(chunk_length)
    i = iter(value)
    while True:
        chunk = list(itertools.islice(i, clen))
        if chunk:
            yield chunk
        else:
            break

@register.filter
def abbreviate(name, pretty=False):
    names = name.split()
    if len(names) == 2:
        return name
    result = [names[0]]
    tiny_name = False
    for surname in names[1:-1]:
        if len(surname) <= 3:
            result.append(surname)
            tiny_name = True
        else:
            if pretty and tiny_name:
                result.append(surname)
            else:
                result.append(surname[0] + '.')
            tiny_name = False
    result.append(names[-1])
    return ' '.join(result)

@register.filter
def getattr (obj, args):
    """ Try to get an attribute from an object.

    Example: {% if block|getattr:"editable,True" %}

    Beware that the default is always a string, if you want this
    to return False, pass an empty second argument:
    {% if block|getattr:"editable," %}
    """
    args = args.split(',')
    if len(args) == 1:
        (attribute, default) = [args[0], '']
    else:
        (attribute, default) = args
    try:
        if callable(obj.__getattribute__(attribute)):
            return obj.__getattribute__(attribute)()
        else:
            return obj.__getattribute__(attribute)
    except AttributeError:
         return  obj.__dict__.get(attribute, default)
    except:
        return default

@register.filter
def leading_zeros(value, desired_digits):
    return str(value).zfill(desired_digits)