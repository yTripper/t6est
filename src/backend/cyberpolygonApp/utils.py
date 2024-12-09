from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import re
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid
import os
from django.conf import settings


class CsrfExemptMixin:
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


def markdown_find_images(markdown_text):
    patterns = r"[^(\s]+\.(?:jpeg|jpg|png|gif)(?=\))"
    return re.findall(patterns, markdown_text)


def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


def upload_image_info(image):
    img_uuid = "{0}-{1}".format(uuid.uuid4().hex[:10], image.name.replace(' ', '-'))
    tmp_file = os.path.join(settings.MARTOR_UPLOAD_PATH, img_uuid)
    def_path = default_storage.save(tmp_file, ContentFile(image.read()))
    img_url = os.path.join(settings.MEDIA_URL, def_path)
    return {
        "img_uuid": img_uuid,
        "img_url": img_url
    }


def upload_image_info(name):
    img_uuid = "{0}-{1}".format(uuid.uuid4().hex[:10], name.replace(' ', '-'))
    tmp_file = os.path.join(settings.MARTOR_UPLOAD_PATH, img_uuid)
    img_url = os.path.join(settings.MEDIA_URL, tmp_file)
    return {
        "img_uuid": img_uuid,
        "img_url": img_url
    }