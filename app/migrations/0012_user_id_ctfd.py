# Generated by Django 2.1.15 on 2020-09-03 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_notifica_notifica_vista'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='id_ctfd',
            field=models.CharField(default='', max_length=10),
        ),
    ]
