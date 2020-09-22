# Generated by Django 2.1.15 on 2020-09-18 10:16

import app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_auto_20200918_0832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sshtunnel_configs',
            name='LOCAL_PORT',
            field=models.IntegerField(default='', validators=[app.models.validate_flag]),
        ),
        migrations.AlterField(
            model_name='sshtunnel_configs',
            name='REMOTE_PORT',
            field=models.IntegerField(default='', validators=[app.models.validate_flag]),
        ),
    ]