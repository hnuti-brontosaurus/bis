# Generated by Django 3.2.14 on 2022-07-26 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0005_locationaccessibility_locationprogram'),
        ('event', '0012_auto_20220726_1019'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventrecord',
            name='number_of_participants',
        ),
        migrations.RemoveField(
            model_name='eventrecord',
            name='number_of_participants_under_26',
        ),
        migrations.RemoveField(
            model_name='vipeventpropagation',
            name='working_days',
        ),
        migrations.RemoveField(
            model_name='vipeventpropagation',
            name='working_hours',
        ),
        migrations.AddField(
            model_name='eventrecord',
            name='working_days',
            field=models.PositiveSmallIntegerField(blank=True, help_text='Pouze pro vícedenní pracovní akce', null=True),
        ),
        migrations.AddField(
            model_name='eventrecord',
            name='working_hours',
            field=models.PositiveSmallIntegerField(blank=True, help_text='Pouze pro vícedenní pracovní akce', null=True),
        ),
        migrations.AlterField(
            model_name='eventpropagation',
            name='diets',
            field=models.ManyToManyField(blank=True, related_name='events', to='categories.DietCategory'),
        ),
    ]