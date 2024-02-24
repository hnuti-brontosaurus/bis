from logging import warning
from os.path import join

import yaml
from django.db.models.fields.related_descriptors import ManyToManyDescriptor
from django.db.models.query_utils import DeferredAttribute
from phonenumber_field.modelfields import PhoneNumberDescriptor
from project.settings import BASE_DIR

with open(join(BASE_DIR, "translation", "model_translations.yaml"), "r") as f:
    model_translations = yaml.safe_load(f)
with open(join(BASE_DIR, "translation", "string_translations.yaml"), "r") as f:
    string_translations = yaml.safe_load(f)

ignored_attr_names = [
    "id",
    "pk",
    "is_superuser",
    "last_login",
    "password",
    "_import",
    "_str",
    "_history",
    "_search",
    "_search_field",
    "_year",
]


def translate_model(model):
    model_name = model.__name__
    if model_name not in model_translations:
        warning(f"There is no translation for model {model_name}")
        return model

    translations = model_translations[model_name]
    model._meta.verbose_name = translations["name"]
    model._meta.verbose_name_plural = translations.get(
        "name_plural", model._meta.verbose_name
    )
    for attr_name in dir(model):
        attr = getattr(model, attr_name)
        if not isinstance(attr, DeferredAttribute):
            if not (isinstance(attr, ManyToManyDescriptor) and not attr.reverse):
                if not isinstance(attr, PhoneNumberDescriptor):
                    continue

        if attr_name.endswith("_id"):
            attr_name = attr_name[:-3]

        if attr_name in ignored_attr_names:
            continue

        if attr_name in (translations.get("fields", dict()) or {}):
            value = translations["fields"][attr_name]

        else:
            try:
                value = _(f"generic.{attr_name}")
            except KeyError:
                warning(
                    f"Model {model_name} has no translation for attribute {attr_name}"
                )
                continue

        if not value:
            continue

        if isinstance(value, str):
            value = [value]

        if isinstance(value, list):
            if len(value) >= 1:
                attr.field.verbose_name = value[0]

            if len(value) >= 2:
                attr.field.help_text = value[1]

    return model


def _(string, **kwargs):
    parts = string.split(".")
    translation = string_translations
    if parts[0] == "models":
        translation = model_translations
        parts.pop(0)
    for part in parts:
        translation = translation[part]

    if isinstance(translation, list):
        translation = translation[0]

    return translation.format(**kwargs)
