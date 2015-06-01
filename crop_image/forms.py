from django import forms
from django.core.urlresolvers import reverse_lazy
from django.db.models.fields import Field
from django.db.models.fields.subclassing import SubfieldBase
import six

from crop_image.widgets import JCropImageWidget, UploadedCropImage


class CropImageFormField(forms.Field):
    """ Form field
    """
    widget = JCropImageWidget

    def __init__(self, *args, **kwargs):
        self.upload_to = kwargs.pop('upload_to', False)
        super(CropImageFormField, self).__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        attrs = super(CropImageFormField, self).widget_attrs(widget)
        if self.upload_to is not None:
            # The HTML attribute is maxlength, not max_length.
            attrs.update({'upload_to': str(self.upload_to)})
        return attrs

    def prepare_value(self, value):
        return super(CropImageFormField, self).prepare_value(value)

    def clean(self, value):
        return value

    def to_python(self, data):
        return data


class CropImageModelField(Field):
    """ Model field
    """
    __metaclass__ = SubfieldBase
    description = "Field to store the cropped image path, the cropping data, and the original image path"

    def __init__(self, upload_to='', url='', *args, **kwargs):
        kwargs['max_length'] = 255
        self.upload_to = upload_to
        super(CropImageModelField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"

    def deconstruct(self):
        name, path, args, kwargs = super(CropImageModelField, self).deconstruct()
        del kwargs["max_length"]
        kwargs["upload_to"] = self.upload_to
        kwargs["url"] = self.url
        return name, path, args, kwargs

    def to_python(self, value):
        if isinstance(value, six.string_types) and value != '':
            return UploadedCropImage(value)
        elif isinstance(value, UploadedCropImage):
            return value

    def get_prep_value(self, value):
        if isinstance(value, UploadedCropImage):
            return value.data

    def formfield(self, **kwargs):
        defaults = {'form_class': CropImageFormField, 'upload_to': self.upload_to}
        defaults.update(kwargs)
        return super(CropImageModelField, self).formfield(**defaults)