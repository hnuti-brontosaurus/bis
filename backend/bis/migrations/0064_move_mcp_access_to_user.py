from django.db import migrations, models


def copy_mcp_access(apps, schema_editor):
    MCPAccess = apps.get_model("bis", "MCPAccess")
    User = apps.get_model("bis", "User")
    for access in MCPAccess.objects.all():
        User.objects.filter(email__iexact=access.email).update(
            is_bot=access.is_bot,
            sees_personal_data_over_mcp=access.sees_personal_data,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("bis", "0063_mcp_access"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_bot",
            field=models.BooleanField(
                default=False,
                help_text="Účet bez člověka a bez schránky: přes MCP vidí data bez ohledu na role a exporty musí posílat na e-mail někoho, kdo vidí vše.",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="sees_personal_data_over_mcp",
            field=models.BooleanField(
                default=False,
                help_text="Jména, kontakty, data narození, adresy a poznámky. Jen pro LLM se smlouvou o zpracování osobních údajů. Zdravotní údaje přes MCP nevidí nikdo.",
            ),
        ),
        migrations.RunPython(copy_mcp_access, migrations.RunPython.noop),
        migrations.DeleteModel(name="MCPAccess"),
    ]
