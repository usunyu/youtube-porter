# Generated by Django 2.1.1 on 2018-10-18 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('porter', '0005_channeljob'),
    ]

    operations = [
        migrations.AddField(
            model_name='porterjob',
            name='part',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='porterjob',
            name='playlist',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='porterjob',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Complete'), (1, 'Partial')], default=0),
        ),
        migrations.AddField(
            model_name='settings',
            name='start_channel_job',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='settings',
            name='start_reset_quota_job',
            field=models.BooleanField(default=False),
        ),
    ]