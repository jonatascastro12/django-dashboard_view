from django_select2.widgets import AutoHeavySelect2Widget, AutoHeavySelect2MultipleWidget


class AutoPhotoHeavySelect2Widget(AutoHeavySelect2Widget):
    def init_options(self):
        super(AutoPhotoHeavySelect2Widget, self).init_options()
        self.options['escapeMarkup'] = "*START*function (markup) { return markup; }*END*"
        self.options['formatSelection'] = "*START*" \
                                            "function(obj){" \
                                            "var $obj = " \
                                            "'<span><img class=\"select-img\" src=\"'+obj.photo+'\"> '+ obj.text +'</span>';" \
                                            "return $obj;" \
                                            "}" \
                                            "*END*"
        self.options['formatResult'] = "*START*" \
                                            "function(obj){" \
                                            "var $obj = " \
                                            "'<span><img class=\"select-img\" src=\"'+obj.photo+'\"> '+ obj.text +'</span>';" \
                                            "return $obj;" \
                                            "}" \
                                            "*END*"

class AutoPhotoHeavySelect2MultipleWidget(AutoHeavySelect2MultipleWidget):
        def init_options(self):
            super(AutoPhotoHeavySelect2MultipleWidget, self).init_options()
            self.options['escapeMarkup'] = "*START*function (markup) { return markup; }*END*"
            self.options['formatSelection'] = "*START*" \
                                                "function(a,b,c){console.log(a);" \
                                                "var $obj = " \
                                                "'<span><img class=\"select-img\" src=\"'+a.photo+'\"> '+ a.text +'</span>';" \
                                                "return $obj;" \
                                                "}" \
                                                "*END*"
            self.options['formatResult'] = "*START*" \
                                                "function(a,b,c){console.log(a);" \
                                                "var $obj = " \
                                                "'<span><img class=\"select-img\" src=\"'+a.photo+'\"> '+ a.text +'</span>';" \
                                                "return $obj;" \
                                                "}" \
                                                "*END*"