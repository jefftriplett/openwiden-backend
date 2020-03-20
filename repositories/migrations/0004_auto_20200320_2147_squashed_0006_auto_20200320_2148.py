# Generated by Django 3.0.2 on 2020-03-20 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repositories', '0003_auto_20200309_1607'),
    ]

    operations = [
        migrations.RenameField(
            model_name='versioncontrolservice',
            old_name='label',
            new_name='host',
        ),
        migrations.RemoveField(
            model_name='versioncontrolservice',
            name='url',
        ),
        migrations.AlterField(
            model_name='versioncontrolservice',
            name='host',
            field=models.CharField(max_length=30, unique=True, verbose_name='host'),
        ),
        migrations.AlterField(
            model_name='versioncontrolservice',
            name='host',
            field=models.CharField(max_length=50, unique=True, verbose_name='host'),
        ),
    ]
