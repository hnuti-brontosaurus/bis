# Generated by Django 3.2.17 on 2023-02-19 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game_book', '0004_alter_game_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]