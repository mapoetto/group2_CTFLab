# Generated by Django 2.1.15 on 2020-09-21 08:14

import app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_statistiche'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistiche',
            name='punteggio',
            field=models.IntegerField(default=0, validators=[app.models.validate_flag]),
        ),
    ]