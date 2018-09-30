# Generated by Django 2.1.1 on 2018-09-30 08:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PorterJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video_url', models.CharField(max_length=256)),
                ('status', models.PositiveSmallIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='VideoTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=64, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='YoutubeAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('secret_file', models.CharField(max_length=256)),
            ],
        ),
        migrations.AddField(
            model_name='video',
            name='tags',
            field=models.ManyToManyField(related_name='videos', to='porter.VideoTag'),
        ),
        migrations.AddField(
            model_name='porterjob',
            name='youtube_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='porter_jobs', to='porter.YoutubeAccount'),
        ),
    ]
