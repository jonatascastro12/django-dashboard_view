from django.conf import settings
from django.forms.widgets import TextInput
from django.template.context import Context
from django.template.loader import get_template
import six
try:
    import json
except ImportError:
    import simplejson as json


class UploadedCropImage():
    data = None
    path = None
    original_path = None
    crop_data = None
    def __init__(self, data=None, path=None, original_path=None, crop_data=None, *args, **kwargs):
        if data is None:
            self.path = path
            self.original_path = original_path
            self.crop_data = crop_data
            self.data = unicode(json.dumps({'path': path, 'original_path': original_path, 'crop_data': crop_data}))
        else:
            if isinstance(data, six.string_types) and data != '':
                try:
                    obj = json.loads(data)
                    self.path = obj['path'] if obj['path'] != "" else settings.DEFAULT_IMAGE
                    self.original_path = obj['original_path']
                    self.crop_data = obj['crop_data']
                    self.data = unicode(data)
                except:
                    self.path = data

    def __unicode__(self):
        return self.path


class JCropImageWidget(TextInput):
    ratio = '1'
    jquery_alias = None
    url = ''

    def __init__(self, *args, **kwargs):
        if 'attrs' in kwargs:
            if 'upload_to' in kwargs['attrs']:
                pass
            if 'ratio' in kwargs['attrs']:
                self.ratio = kwargs['attrs'].pop('ratio')
            if 'jquery_alias' in kwargs['attrs']:
                self.jquery_alias = kwargs['attrs'].pop('jquery_alias')
            if 'url' in kwargs['attrs']:
                self.url = kwargs['attrs'].pop('url')

        return super(JCropImageWidget, self).__init__(*args, **kwargs)

    def value_from_datadict(self, data, files, name):
        out = UploadedCropImage(path=data.get(name, ''), original_path=data.get(name+'_original', ''),
                                crop_data=data.get(name+'_crop_data', ''))
        return out.data

    def render(self, name, value, attrs=None):
        if isinstance(value, six.string_types) and value != '':
            value = UploadedCropImage(data=value)
        t = get_template("jcrop/jcrop_image_widget.html")
        substitutions = {
            "upload_url": self.attrs.get('url', False),
            "input_name": name,
            "image_value": value if value is not None else '',
            "image_crop_data_value": value.crop_data if value is not None else '',
            "image_original_value": value.original_path if value is not None else '',
            "upload_to": attrs['upload_to'] if 'upload_to' in attrs else '',
            "ratio": self.ratio,
            "jquery_alias": self.jquery_alias,
            "MEDIA_URL": settings.MEDIA_URL,
            "JCROP_IMAGE_THUMBNAIL_DIMENSIONS": getattr(
                settings, "JCROP_IMAGE_THUMBNAIL_DIMENSIONS", "62x62"
            ),
            "JCROP_IMAGE_WIDGET_DIMENSIONS": getattr(
                settings, "JCROP_IMAGE_WIDGET_DIMENSIONS", "320x320"
            ),
        }
        c = Context(substitutions)

        return t.render(c)

    class Media:
        css = {
            'all': ('css/jquery.Jcrop.min.css', ),
        }
        js = ('js/jquery.color.js', 'js/jquery.Jcrop.min.js', )
