# Generated by Django 3.0.5 on 2020-05-02 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0002_auto_20200502_2019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='avatar_url',
            field=models.URLField(blank=True, null=True, verbose_name='avatar url'),
        ),
    ]
