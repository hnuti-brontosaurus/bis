# Generated by Django 3.2.17 on 2023-02-18 15:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("game_book_categories", "0004_auto_20230208_0027"),
    ]

    operations = [
        migrations.AddField(
            model_name="gamelengthcategory",
            name="emoji",
            field=models.CharField(default="", max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="locationcategory",
            name="emoji",
            field=models.CharField(default="", max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="materialrequirementcategory",
            name="emoji",
            field=models.CharField(default="", max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="mentalcategory",
            name="emoji",
            field=models.CharField(default="", max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="organizersnumbercategory",
            name="emoji",
            field=models.CharField(default="", max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="participantagecategory",
            name="emoji",
            field=models.CharField(default="", max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="participantnumbercategory",
            name="emoji",
            field=models.CharField(default="", max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="physicalcategory",
            name="emoji",
            field=models.CharField(default="", max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="preparationlengthcategory",
            name="emoji",
            field=models.CharField(default="", max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="tag",
            name="emoji",
            field=models.CharField(default="", max_length=1),
            preserve_default=False,
        ),
    ]
