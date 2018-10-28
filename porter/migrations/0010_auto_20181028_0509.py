# Generated by Django 2.1.1 on 2018-10-28 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('porter', '0009_porterjob_retried'),
    ]

    operations = [
        migrations.AddField(
            model_name='porterjob',
            name='comments',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='porterjob',
            name='download_url',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='porterjob',
            name='likes',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='porterjob',
            name='shares',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='porterjob',
            name='views',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='channeljob',
            name='video_source',
            field=models.PositiveSmallIntegerField(choices=[(0, '哔哩哔哩'), (1, '优酷'), (2, '爱奇艺')], default=0),
        ),
        migrations.AlterField(
            model_name='porterjob',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Complete'), (1, 'Partial'), (2, 'Merge')], default=0),
        ),
        migrations.AlterField(
            model_name='porterjob',
            name='video_source',
            field=models.PositiveSmallIntegerField(choices=[(0, '哔哩哔哩'), (1, '优酷'), (2, '爱奇艺'), (3, '抖音'), (4, '美拍'), (5, '快手'), (6, '火山')], default=0),
        ),
    ]