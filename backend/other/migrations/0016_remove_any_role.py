from django.db import migrations


def remove_any_role(apps, schema_editor):
    RoleCategory = apps.get_model("categories", "RoleCategory")
    DashboardItem = apps.get_model("other", "DashboardItem")

    any_role = RoleCategory.objects.filter(slug="any").first()
    if any_role is None:
        return

    for item in DashboardItem.objects.filter(for_roles=any_role):
        item.for_roles.clear()

    any_role.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("other", "0015_announcement"),
        ("categories", "0019_remove_fundraisingcampaigncategory"),
    ]

    operations = [migrations.RunPython(remove_any_role, migrations.RunPython.noop)]
