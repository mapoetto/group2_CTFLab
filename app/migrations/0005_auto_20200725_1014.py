# Generated by Django 2.1.15 on 2020-07-25 10:14

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_lab'),
    ]

    operations = [
        migrations.AddField(
            model_name='lab',
            name='dockerfile',
            field=models.TextField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='lab',
            name='descrizione',
            field=models.TextField(),
        ),
    ]