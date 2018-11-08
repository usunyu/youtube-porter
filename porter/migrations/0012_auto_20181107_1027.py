# Generated by Django 2.1.1 on 2018-11-07 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('porter', '0011_settings_start_kuaiyinshi_recommend_job'),
    ]

    operations = [
        migrations.AddField(
            model_name='porterjob',
            name='thumbnail_file',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='porterjob',
            name='thumbnail_status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Default'), (1, 'Skipped'), (2, 'Updated'), (3, 'Failed')], default=0),
        ),
        migrations.AddField(
            model_name='porterjob',
            name='thumbnail_url',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
