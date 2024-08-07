# Generated by Django 4.1.8 on 2023-12-26 08:38
from os.path import join

from django.conf import settings
from django.db import migrations
from PIL import Image, UnidentifiedImageError


def migrate(apps, schema_editor):
    EventPropagationImage = apps.get_model("event", "EventPropagationImage")

    for image in EventPropagationImage.objects.all():
        if file := getattr(image, "image"):
            file_path = join(settings.MEDIA_ROOT, file.name)
            try:
                image = Image.open(file_path)
            except UnidentifiedImageError:
                image = None

            max_size = 1920
            if image and (image.width > max_size or image.height > max_size):
                try:
                    image = image.copy()
                    image.thumbnail((max_size, max_size))
                    image.save(file_path)
                    continue
                except (OSError, ValueError):
                    pass


class Migration(migrations.Migration):
    dependencies = [
        ("bis", "0030_remove_eycacard_photo_user_photo"),
    ]

    operations = [migrations.RunPython(migrate, migrations.RunPython.noop)]
