# Generated by Django 2.2 on 2020-06-26 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datavalidation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='validator',
            name='last_run_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
