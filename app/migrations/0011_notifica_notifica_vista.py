# Generated by Django 2.1.15 on 2020-09-02 09:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_auto_20200901_0951'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notifica',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('testo', models.CharField(max_length=120)),
                ('link', models.CharField(max_length=220)),
                ('destinatario', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Notifica_vista',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stato', models.CharField(max_length=120)),
                ('notifica_id', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifica_id', to='app.Notifica')),
                ('user_id', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_id', to='app.User')),
            ],
        ),
    ]
