# Generated by Django 3.0.5 on 2020-05-22 22:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repositories', '0004_auto_20200509_1813'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='description'),
        ),
    ]
