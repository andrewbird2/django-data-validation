# Generated by Django 2.2 on 2020-06-26 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datavalidation', '0002_auto_20200626_2208'),
    ]

    operations = [
        migrations.AddField(
            model_name='validator',
            name='exc_obj_pk',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='validator',
            name='exc_type',
            field=models.CharField(blank=True, default=None, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='validator',
            name='traceback',
            field=models.TextField(blank=True, default=None, max_length=2000, null=True),
        ),
    ]