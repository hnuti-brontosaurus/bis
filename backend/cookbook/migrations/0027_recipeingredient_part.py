from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cookbook", "0026_alter_recipestep_photo"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipeingredient",
            name="part",
            field=models.CharField(blank=True, max_length=63),
        ),
    ]
