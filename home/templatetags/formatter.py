from django import template
#from django.contrib.humanize.templatetags.humanize import intcomma
from datetime import timedelta
from django.utils import timezone
from django.utils.safestring import mark_safe
import os
import base64

register = template.Library()

@register.filter
def encodeb64(value):
    return base64.b64encode(str(value).encode()).decode()