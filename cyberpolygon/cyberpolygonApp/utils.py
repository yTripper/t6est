from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import re

class CsrfExemptMixin:
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
def markdown_find_images(markdown_text):
    """
    return list of image urls inside `markdown_text`.
    :param `markdown_text` is markdown text to find.

    example markdown text:
        Hello ![title](/path/to/image.png)
    provides for:
        jpeg|jpg|png|gif
    demo:
        https://regex101.com/r/uc3XfV/1
    """
    patterns = r"[^(\s]+\.(?:jpeg|jpg|png|gif)(?=\))"
    return re.findall(patterns, markdown_text)

def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None