from django.utils.module_loading import autodiscover_modules
from dashboard_view import dashboard_site

def autodiscover():
    autodiscover_modules('dashboard', register_to=dashboard_site)

default_app_config = 'django.contrib.admin.apps.AdminConfig'
