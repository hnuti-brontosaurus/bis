from html import unescape

from django import template
from django.utils.html import strip_tags

register = template.Library()


@register.filter
def plain_text(html):
    return unescape(strip_tags(html))
