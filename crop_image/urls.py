from django.conf.urls import patterns, url

from crop_image.views import image_upload


urlpatterns = patterns('',
    url(r'^upload_photo$', image_upload, name="upload_photo"),
)

