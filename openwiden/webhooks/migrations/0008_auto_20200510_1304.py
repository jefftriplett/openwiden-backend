# Generated by Django 3.0.5 on 2020-05-10 13:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('repositories', '0004_auto_20200509_1813'),
        ('webhooks', '0007_auto_20200510_1221'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='repositorywebhook',
            name='unique_repository_webhook',
        ),
        migrations.AlterField(
            model_name='repositorywebhook',
            name='repository',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='webhook', to='repositories.Repository', verbose_name='repository'),
        ),
    ]
