# Generated by Django 2.1.15 on 2020-07-09 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20200708_1548'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'Username già utilizzato'}, max_length=120, unique=True),
        ),
    ]