# Generated by Django 2.1.15 on 2020-08-04 17:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_lab_args'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lab',
            name='args',
        ),
        migrations.AddField(
            model_name='lab',
            name='argomento_1',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='argo1', to='app.Tag_Args'),
        ),
        migrations.AddField(
            model_name='lab',
            name='argomento_2',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='argo2', to='app.Tag_Args'),
        ),
        migrations.AddField(
            model_name='lab',
            name='argomento_3',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='argo3', to='app.Tag_Args'),
        ),
        migrations.AddField(
            model_name='lab',
            name='argomento_4',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='argo4', to='app.Tag_Args'),
        ),
    ]
