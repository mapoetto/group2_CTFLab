# Generated by Django 2.1.15 on 2020-09-25 17:09

import app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0024_auto_20200925_0723'),
    ]

    operations = [
        migrations.AddField(
            model_name='lab',
            name='durata_secondi',
            field=models.IntegerField(default=3600, validators=[app.models.validate_flag], verbose_name='Durata massima in secondi'),
        ),
    ]
