import base64
import binascii
import re
from typing import TypedDict

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from rest_framework.exceptions import ValidationError
from rest_framework.fields import FileField, ImageField
from rest_framework.pagination import PageNumberPagination
from rest_framework.serializers import ModelSerializer

from common.thumbnails import get_thumbnail_path, ThumbnailImageField


class Pagination(PageNumberPagination):
    page_size_query_param = 'page_size'


def parse_request_data(serializer_class, data_name='data'):
    def decorator(fn):
        def wrapper(request, *args, **kwargs):
            serializer = serializer_class(data=getattr(request, data_name))
            serializer.is_valid(raise_exception=True)
            return fn(request, serializer.validated_data, *args, **kwargs)

        return wrapper

    return decorator


def catch_related_object_does_not_exist(fn):
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except AttributeError as e:
            raise ValidationError(str(e))

    return wrapper


class Base64FieldMixin:
    EMPTY_VALUES = None, "", [], (), {}

    def to_internal_value(self, base64_data):
        try:
            assert isinstance(base64_data, str), 'Expects base64 string'
            assert ";base64," in base64_data, '";base64," not in data'
            header, base64_data = base64_data.split(";base64,", 1)
            assert re.match(r'data:\w+/\w+;filename=.*', header), 'header does not match "data:\w+/\w+;filename=.*"'
            header = header[5:]
            content_type, filename = header.split(';')
            filename = filename.split('=', 1)[1]
            extension = content_type.split('/', 1)[1]

        except AssertionError as e:
            raise ValidationError(e)

        try:
            decoded_file = base64.b64decode(base64_data)
        except (TypeError, binascii.Error, ValueError) as e:
            raise ValidationError(e)

        complete_file_name = filename + "." + extension
        data = SimpleUploadedFile(
            name=complete_file_name,
            content=decoded_file,
            content_type=content_type
        )

        return super().to_internal_value(data)


class Base64ImageField(Base64FieldMixin, ImageField):
    pass


class ThumbnailedBase64ImageField(Base64ImageField):
    UrlsType = TypedDict('UrlsType', {size: str for size in list(settings.THUMBNAIL_SIZES.keys()) + ['original']})

    def to_representation(self, value) -> UrlsType:
        if not value:
            return None

        try:
            url = value.url
            name = value.name
        except AttributeError:
            return None

        urls = {
            size: '/media/' + get_thumbnail_path(name, size) for size in settings.THUMBNAIL_SIZES
        }
        urls['original'] = url

        request = self.context.get('request', None)
        if request:
            for key, value in urls.items():
                urls[key] = request.build_absolute_uri(value)

        return urls


class Base64FileField(Base64FieldMixin, FileField):
    pass


ModelSerializer.serializer_field_mapping[models.ImageField] = Base64ImageField
ModelSerializer.serializer_field_mapping[ThumbnailImageField] = ThumbnailedBase64ImageField
ModelSerializer.serializer_field_mapping[models.FileField] = Base64FileField
