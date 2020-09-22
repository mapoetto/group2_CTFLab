# Generated by Django 2.1.15 on 2020-09-18 08:32

import app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_auto_20200918_0831'),
    ]

    operations = [
        migrations.AddField(
            model_name='sshtunnel_configs',
            name='DNS_NAME_SERVER',
            field=models.CharField(default='', max_length=220),
        ),
        migrations.AddField(
            model_name='sshtunnel_configs',
            name='FULL_PATH_SSH_KEY',
            field=models.CharField(default='', max_length=220),
        ),
        migrations.AddField(
            model_name='sshtunnel_configs',
            name='LOCAL_PORT',
            field=models.IntegerField(default=0, validators=[app.models.validate_flag]),
        ),
        migrations.AddField(
            model_name='sshtunnel_configs',
            name='REMOTE_PORT',
            field=models.IntegerField(default=0, validators=[app.models.validate_flag]),
        ),
        migrations.AddField(
            model_name='sshtunnel_configs',
            name='USER_SERVER',
            field=models.CharField(default='', max_length=64),
        ),
    ]
