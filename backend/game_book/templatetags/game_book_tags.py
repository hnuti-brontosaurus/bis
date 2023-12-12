from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def verbose(context, field):
    return context["object"]._meta.get_field(field).verbose_name


@register.inclusion_tag("game_book/game_detail_field.html", takes_context=True)
def game_detail_field(context, field, extra=None):
    name = verbose(context, field)
    value = getattr(context["object"], field)

    if extra == "count" and value:
        value = str(value.count())

    if extra == "join":
        value = ", ".join(str(value) for value in value.all())

    value = mark_safe(value)

    if field.endswith("_category"):
        help_text = getattr(context["object"], field.replace("_category", "_note"))
    return locals()


@register.inclusion_tag("game_book/category_emoji.html")
def category_emoji(c, extra=None):
    return locals()
