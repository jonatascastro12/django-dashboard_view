from django_select2.media import django_select2_static, get_select2_js_libs, DEBUG
from django.templatetags.static import static

def django_select2_static(file):
    return static('django_select2_extension/' + file)

def get_select2_extended_heavy_js_libs():
    libs = get_select2_js_libs()

    if DEBUG:
        js_file = 'js/heavy_data_extended.js'
    else:
        js_file = 'js/heavy_data_extended.js'
    return libs + (django_select2_static(js_file), )