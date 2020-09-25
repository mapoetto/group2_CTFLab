# Generated by Django 2.1.15 on 2020-09-25 07:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_auto_20200921_1451'),
    ]

    operations = [
        migrations.AddField(
            model_name='lab',
            name='argomento_10',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='argo10', to='app.Tag_Args'),
        ),
        migrations.AddField(
            model_name='lab',
            name='argomento_11',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='argo11', to='app.Tag_Args'),
        ),
        migrations.AddField(
            model_name='lab',
            name='argomento_5',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='argo5', to='app.Tag_Args'),
        ),
        migrations.AddField(
            model_name='lab',
            name='argomento_6',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='argo6', to='app.Tag_Args'),
        ),
        migrations.AddField(
            model_name='lab',
            name='argomento_7',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='argo7', to='app.Tag_Args'),
        ),
        migrations.AddField(
            model_name='lab',
            name='argomento_8',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='argo8', to='app.Tag_Args'),
        ),
        migrations.AddField(
            model_name='lab',
            name='argomento_9',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='argo9', to='app.Tag_Args'),
        ),
    ]
