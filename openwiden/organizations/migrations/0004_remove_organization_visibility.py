# Generated by Django 3.0.7 on 2020-08-09 11:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0003_auto_20200509_1921'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='visibility',
        ),
    ]