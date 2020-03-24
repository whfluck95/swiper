import json

from django.http import HttpResponse
from django.conf import settings

from common.stat import OK


def render_json(data=None, code=OK):
    result = {
        'data': data,
        'code': code
    }

    if settings.DEBUG:
        json_result = json.dumps(result, ensure_ascii=False, indent=4, sort_keys=True)
    else:
        json_result = json.dumps(result, ensure_ascii=False, separators=(',', ':'))

    return HttpResponse(json_result)