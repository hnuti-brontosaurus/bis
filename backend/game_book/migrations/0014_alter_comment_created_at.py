# Generated by Django 4.1.8 on 2023-12-06 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game_book', '0013_alter_comment_is_hidden'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]