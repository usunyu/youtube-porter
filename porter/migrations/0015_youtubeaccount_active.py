# Generated by Django 2.1.1 on 2018-11-19 01:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('porter', '0014_auto_20181114_0321'),
    ]

    operations = [
        migrations.AddField(
            model_name='youtubeaccount',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]