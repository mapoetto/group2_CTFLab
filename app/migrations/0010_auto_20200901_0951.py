# Generated by Django 2.1.15 on 2020-09-01 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20200901_0950'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='porta_vpn',
            field=models.CharField(default='', max_length=10),
        ),
    ]
