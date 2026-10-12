import os
from os import makedirs, symlink
from os.path import dirname, exists, join, splitext

from django.conf import settings
from django.db.models import ImageField, signals
from django.db.models.fields.files import ImageFieldFile
from PIL import Image, UnidentifiedImageError


def get_thumbnail_path(file_name, size_name):
    file_name, file_extension = splitext(file_name)
    return join("thumbnails", f"{file_name}_{size_name}{file_extension}")


class ThumbnailImageFieldFile(ImageFieldFile):
    def resize_original_image(self, size_name):
        if not self:
            return

        try:
            size = settings.THUMBNAIL_SIZES[size_name]
        except KeyError:
            raise ValueError(
                f"Thumbnail size '{size_name}' is not defined in THUMBNAIL_SIZES."
            )

        try:
            image = Image.open(self.path)
        except (UnidentifiedImageError, FileNotFoundError):
            return

        if not image or (image.width <= size and image.height <= size):
            return

        try:
            image.thumbnail((size, size))
            image.save(self.path)
        except (OSError, ValueError):
            return

        self.field.do_remove_thumbnails(self.name)
        self.field.make_thumbnails(self)


class ThumbnailImageField(ImageField):
    attr_class = ThumbnailImageFieldFile

    def contribute_to_class(self, cls, name, **kwargs):
        old_init = cls.__init__

        def new_init(_self, *args, **kwargs):
            old_init(_self, *args, **kwargs)
            # Reading a deferred field reloads it into a new instance, whose
            # __init__ would read its own deferred copy again, endlessly.
            if name in _self.get_deferred_fields():
                setattr(_self, f"old_{name}", None)
                return
            # The name, not the file: saving renames the very same FieldFile
            # in place, so an upload passed to the constructor would compare
            # equal to itself and never get thumbnails.
            file = getattr(_self, name)
            setattr(_self, f"old_{name}", (file.name or "") if file._committed else "")

        cls.__init__ = new_init

        super().contribute_to_class(cls, name, **kwargs)
        if not cls._meta.abstract:
            signals.post_save.connect(self.update_thumbnails, sender=cls)
            signals.post_delete.connect(self.remove_thumbnails, sender=cls)

    def update_thumbnails(self, instance, **kwargs):
        old_name = getattr(instance, f"old_{self.attname}")
        # Still deferred: the photo was neither read nor assigned, so it is
        # unchanged, and reading it here would cost a query.
        if old_name is None and self.attname in instance.get_deferred_fields():
            return

        file = getattr(instance, self.attname)
        # Every save of the row lands here, and re-rendering an unchanged
        # photo would also fail whenever its original is missing on disk.
        if (old_name or "") == (file.name or ""):
            return

        self.do_remove_thumbnails(old_name)
        self.make_thumbnails(file)
        setattr(instance, f"old_{self.attname}", file.name)

    def make_thumbnails(self, file):
        if not file:
            return

        missing = {}
        for size_name, size in settings.THUMBNAIL_SIZES.items():
            path = join(settings.MEDIA_ROOT, get_thumbnail_path(file.name, size_name))
            if not exists(path):
                missing[path] = size
        if not missing:
            return

        file_path = join(settings.MEDIA_ROOT, file.name)
        try:
            image = Image.open(file_path)
        except UnidentifiedImageError:
            image = None

        for thumbnail_path, size in missing.items():
            makedirs(dirname(thumbnail_path), exist_ok=True)
            if image and (image.width > size or image.height > size):
                try:
                    new = image.copy()
                    new.thumbnail((size, size))
                    new.save(thumbnail_path)
                    continue
                except (OSError, ValueError):
                    pass

            symlink(file_path, thumbnail_path)

    def remove_thumbnails(self, instance, **kwargs):
        self.do_remove_thumbnails(getattr(instance, self.attname).name)

    @staticmethod
    def do_remove_thumbnails(file_name):
        if not file_name:
            return

        for size_name in settings.THUMBNAIL_SIZES:
            thumbnail_path = join(
                settings.MEDIA_ROOT, get_thumbnail_path(file_name, size_name)
            )

            if exists(thumbnail_path):
                os.remove(thumbnail_path)
