import django.db.models.deletion
from django.db import migrations, models


def copy_campaigns(apps, schema_editor):
    OldModel = apps.get_model("categories", "FundraisingCampaignCategory")
    NewModel = apps.get_model("donations", "FundraisingCampaign")
    for old in OldModel.objects.all():
        NewModel.objects.create(id=old.id, name=old.name, slug=old.slug)


class Migration(migrations.Migration):
    dependencies = [
        ("categories", "0018_fundraisingcampaigncategory"),
        ("donations", "0011_delete_removed_from_campaign_category"),
    ]

    operations = [
        migrations.CreateModel(
            name="FundraisingCampaign",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=63)),
                ("slug", models.SlugField(unique=True)),
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.RunPython(copy_campaigns, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="donorevent",
            name="campaign",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="events",
                to="donations.fundraisingcampaign",
            ),
        ),
    ]
