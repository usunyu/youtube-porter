# Generated by Django 2.1.1 on 2018-10-16 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('porter', '0003_youtubeaccount_upload_quota'),
    ]

    operations = [
        migrations.AddField(
            model_name='youtubeaccount',
            name='channel',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='youtubeaccount',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
