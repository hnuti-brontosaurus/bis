import os
from os import symlink, makedirs
from os.path import splitext, join, exists

from PIL import Image, UnidentifiedImageError
from django.conf import settings
from django.db.models import ImageField
from django.db.models import signals


def get_thumbnail_path(file_name, size_name):
    file_name, file_extension = splitext(file_name)
    return join('thumbnails', f"{file_name}_{size_name}{file_extension}")


class ThumbnailImageField(ImageField):
    def contribute_to_class(self, cls, name, **kwargs):
        old_init = cls.__init__
        def new_init(_self, *args, **kwargs):
            old_init(_self, *args, **kwargs)
            setattr(_self, f'old_{name}', getattr(_self, name))

        cls.__init__ = new_init

        super().contribute_to_class(cls, name, **kwargs)
        if not cls._meta.abstract:
            signals.post_save.connect(self.create_thumbnails, sender=cls)
            signals.post_delete.connect(self.remove_thumbnails, sender=cls)

    def create_thumbnails(self, instance, **kwargs):
        old_file = getattr(instance, f"old_{self.attname}")
        self.do_remove_thumbnails(old_file)

        if file := getattr(instance, self.attname):
            thumbnail_dir_path = join(settings.BASE_DIR, 'media', 'thumbnails', self.upload_to)
            makedirs(thumbnail_dir_path, exist_ok=True)

            file_path = join(settings.MEDIA_ROOT, file.name)
            try:
                image = Image.open(file_path)
            except UnidentifiedImageError:
                image = None

            for size_name, size in settings.THUMBNAIL_SIZES.items():
                thumbnail_path = join(settings.MEDIA_ROOT, get_thumbnail_path(file.name, size_name))

                if exists(thumbnail_path):
                    continue

                if image and (image.width >= size or image.height >= size):
                    try:
                        new = image.copy()
                        new.thumbnail((size, size))
                        new.save(thumbnail_path)
                        continue
                    except (OSError, ValueError):
                        pass

                symlink(file_path, thumbnail_path)

    def remove_thumbnails(self, instance, **kwargs):
        self.do_remove_thumbnails(getattr(instance, self.attname))

    @staticmethod
    def do_remove_thumbnails(file):
        if not file: return

        for size_name, size in settings.THUMBNAIL_SIZES.items():
            thumbnail_path = join(settings.MEDIA_ROOT, get_thumbnail_path(file.name, size_name))

            if exists(thumbnail_path):
                os.remove(thumbnail_path)
