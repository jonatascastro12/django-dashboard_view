from itertools import chain
import json
from django import forms
from django.conf import settings
from django.utils.encoding import force_text
from django_select2.media import get_select2_css_libs
from django_select2.widgets import AutoHeavySelect2Widget, AutoHeavySelect2MultipleWidget, logger
from django_select2_extension.media import get_select2_extended_heavy_js_libs

class NewAutoHeavySelect2Widget(AutoHeavySelect2Widget):
    def init_options(self):
        super(NewAutoHeavySelect2Widget, self).init_options()
        self.options['minimumInputLength'] = 0

class NewAutoHeavySelect2MultipleWidget(AutoHeavySelect2MultipleWidget):
    def init_options(self):
        super(AutoHeavySelect2MultipleWidget, self).init_options()
        self.options['minimumInputLength'] = 0

class Select2WithPhotoMixin(object):
    def init_options(self):
        super(Select2WithPhotoMixin, self).init_options()
        self.options['minimumInputLength'] = 0
        self.options['escapeMarkup'] = "*START*function (markup) { return markup; }*END*"
        self.options['formatSelection'] = "*START*" \
                                            "function(a,b,c){console.log(a);" \
                                          " if (typeof a.text === 'object'){" \
                                          "var $obj = " \
                                           "'<span><img class=\"select-img\" src=\"'+a.text['photo']+'\"> '+ a.text['txt'] +'</span>';" \
                                          "}else{" \
                                            "var $obj = " \
                                            "'<span><img class=\"select-img\" src=\"'+a.photo+'\"> '+ a.text +'</span>';};" \
                                            "return $obj;" \
                                            "}" \
                                            "*END*"
        self.options['formatResult'] = "*START*" \
                                            "function(a,b,c){console.log(a);" \
                                          " if (typeof a.text === 'object'){" \
                                          "var $obj = " \
                                           "'<span><img class=\"select-img\" src=\"'+a.text['photo']+'\"> '+ a.text['txt'] +'</span>';" \
                                          "}else{" \
                                            "var $obj = " \
                                            "'<span><img class=\"select-img\" src=\"'+a.photo+'\"> '+ a.text +'</span>';};" \
                                            "return $obj;" \
                                            "}" \
                                            "*END*"

    def render_texts(self, selected_choices, choices):
        """
        Renders a JS array with labels for the ``selected_choices``.

        :param selected_choices: List of selected choices' values.
        :type selected_choices: :py:obj:`list` or :py:obj:`tuple`

        :param choices: Extra choices, if any. This is a list of tuples. In each tuple, the first
            item is the choice value and the second item is choice label.
        :type choices: :py:obj:`list` or :py:obj:`tuple`

        :return: The rendered JS array code.
        :rtype: :py:obj:`unicode`
        """
        selected_choices = list(force_text(v) for v in selected_choices)
        txts = []
        all_choices = choices if choices else []
        choices_dict = dict()
        self_choices = self.choices

        from django_select2_extension import fields
        if isinstance(self_choices, fields.FilterableAdvancedModelChoiceIterator):
            self_choices.set_extra_filter(**{'%s__in' % self.field.get_pk_field_name(): selected_choices})

        values = chain(self_choices, all_choices)

        for v in values:
            if len(v)==2:
                val = force_text(v[0])
                choices_dict[val] = {'txt': v[1], 'photo': None}
            else:
                val = force_text(v[0])
                choices_dict[val] = {'txt': v[1], 'photo': v[2].get_small_thumbnail()}

        for val in selected_choices:
            try:
                txts.append(choices_dict[val])
            except KeyError:
                logger.error("Value '%s' is not a valid choice.", val)

        if hasattr(self.field, '_get_val_txt') and selected_choices:
            for val in selected_choices:
                txt = self.field._get_val_txt(val)
                if txt is not None:
                    txts.append(txt)
        if txts:
            return json.dumps(txts)

    def _get_media(self):
        """
        Construct Media as a dynamic property

        This is essential because we need to check RENDER_SELECT2_STATICS
        before returning our assets.

        for more information:
        https://docs.djangoproject.com/en/1.8/topics/forms/media/#media-as-a-dynamic-property
        """
        if getattr(settings, 'AUTO_RENDER_SELECT2_STATICS', True):
            return forms.Media(
                js=get_select2_extended_heavy_js_libs(),
                css={'screen': get_select2_css_libs()}
            )
        return forms.Media()
    media = property(_get_media)

    class Media:
        js = get_select2_extended_heavy_js_libs()
        css = {
            'screen': get_select2_css_libs()
        }

class AutoPhotoHeavySelect2Widget(Select2WithPhotoMixin, AutoHeavySelect2Widget):
    pass



class AutoPhotoHeavySelect2MultipleWidget(Select2WithPhotoMixin, AutoHeavySelect2MultipleWidget):
    pass