# Generated by Django 4.1.8 on 2024-01-22 09:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("categories", "0013_opportunitypriority"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="eventcategory",
            options={"ordering": ("order",)},
        ),
        migrations.AddField(
            model_name="eventcategory",
            name="order",
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
