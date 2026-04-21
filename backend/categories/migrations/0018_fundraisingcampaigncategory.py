from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("categories", "0017_donoreventcategory"),
    ]

    operations = [
        migrations.CreateModel(
            name="FundraisingCampaignCategory",
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
    ]
