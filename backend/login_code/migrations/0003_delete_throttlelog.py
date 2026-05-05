from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("login_code", "0002_alter_throttlelog_created"),
    ]

    operations = [
        migrations.DeleteModel(name="ThrottleLog"),
    ]
