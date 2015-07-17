import imghdr
import json
import os
from PIL import Image
from django.conf import settings
from django.core.files.storage import default_storage
from django.http.response import HttpResponse
from dashboard_view import errors

# Create your views here.
def image_upload(request):
    upload_to = ''
    if 'upload_to' in request.POST:
        upload_to = request.POST['upload_to']

    if request.POST and 'crop_data' in request.POST and 'original' in request.POST:

        file = default_storage.open(os.path.join(settings.MEDIA_ROOT, request.POST['original']))
        im = Image.open(file)

        crop_data = json.loads(request.POST['crop_data'])
        img_ratio = im.size[0]/float(crop_data["bounds"][0])

        crop_params = (int(round(crop_data['selectionPosition']['left']*img_ratio)),
                       int(round(crop_data['selectionPosition']['top']*img_ratio)),
                       int(round(crop_data['selectionPosition']['left']*img_ratio))+int(round(crop_data['selectionSize']*img_ratio)),
                       int(round(crop_data['selectionPosition']['top']*img_ratio))+int(round(crop_data['selectionSize']*img_ratio))
        )

        thumb_posfix = '_thumb_512'

        original_name, extension = os.path.splitext(im.fp.name)
        im = im.crop(crop_params)
        im.thumbnail((512, 512))

        newfilename = original_name + thumb_posfix + extension
        newfile = default_storage.open(newfilename, 'wb')

        im.save(newfile, "JPEG")
        newfile.close()
        url = os.path.normpath(os.path.join(upload_to, os.path.split(newfile.name)[1]))

        return HttpResponse(url)

    if request.FILES and 'photo' in request.FILES:
        upload_full_path = os.path.join(settings.MEDIA_ROOT, upload_to)
        path = default_storage.save(os.path.join(upload_full_path, request.FILES['photo'].name), request.FILES['photo'])
        url = os.path.normpath(os.path.join(upload_to, os.path.split(path)[1]))

        try:
            im = Image.open(path)
            if im.format not in ('JPEG', 'JPG', 'PNG'):
                default_storage.delete(path)
                return HttpResponse(status=406, content=errors.ImageNotJpgOrPngError().response_error())
            if (im.size <= (512,512)):
                im.close()
                default_storage.delete(path)
                return HttpResponse(status=406, content=errors.ImageLessThan512().response_error())
        except IOError:
            return HttpResponse(status=406, content=errors.ImageNotRecognized().response_error())

        return HttpResponse(url)
    return HttpResponse(status=405, content_type='application/json', content=errors.GetRequestNotPermitted.response_error())