# Generated by Django 3.0.2 on 2020-03-09 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repositories', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='versioncontrolservice',
            name='label',
            field=models.CharField(default='', max_length=30, verbose_name='label'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='versioncontrolservice',
            name='name',
            field=models.CharField(max_length=100, verbose_name='name'),
        ),
    ]