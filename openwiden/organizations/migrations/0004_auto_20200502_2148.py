# Generated by Django 3.0.5 on 2020-05-02 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0003_auto_20200502_2146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='created_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='created at'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='updated_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='updated at'),
        ),
    ]
