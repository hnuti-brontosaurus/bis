from django import template
from tinymce.models import HTMLField
from tinymce.widgets import TinyMCE

register = template.Library()


@register.filter
def is_rich_text(field):
    return isinstance(field.field.widget, TinyMCE)


@register.simple_tag(takes_context=True)
def verbose(context, field):
    return context["object"]._meta.get_field(field).verbose_name


@register.inclusion_tag("game_book/game_fact.html", takes_context=True)
def game_fact(context, field):
    game = context["object"]
    value = getattr(game, field)
    return {
        "name": verbose(context, field),
        "categories": (
            value.all() if game._meta.get_field(field).many_to_many else [value]
        ),
        "note": getattr(game, field.replace("_category", "_note")),
    }


@register.inclusion_tag("game_book/game_section.html", takes_context=True)
def game_section(context, field):
    game = context["object"]
    return {
        "name": verbose(context, field),
        "value": getattr(game, field),
        "is_html": isinstance(game._meta.get_field(field), HTMLField),
    }


@register.inclusion_tag("game_book/category_emoji.html")
def category_emoji(c, extra=None):
    return locals()
