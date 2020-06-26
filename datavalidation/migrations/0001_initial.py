# Generated by Django 2.2 on 2020-06-26 21:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Summary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name_plural': 'summaries',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Validator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method_name', models.CharField(max_length=80)),
                ('description', models.TextField(max_length=100)),
                ('is_class_method', models.BooleanField()),
                ('last_run_time', models.DateTimeField()),
                ('passed', models.BooleanField(blank=True, null=True)),
                ('num_passed', models.PositiveIntegerField(blank=True, null=True)),
                ('num_failed', models.PositiveIntegerField(blank=True, null=True)),
                ('num_na', models.PositiveIntegerField(blank=True, null=True)),
                ('num_allowed_to_fail', models.PositiveIntegerField(blank=True, null=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contenttypes.ContentType')),
            ],
            options={
                'unique_together': {('content_type', 'method_name')},
                'index_together': {('content_type', 'method_name')},
            },
        ),
        migrations.CreateModel(
            name='FailingObjects',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_pk', models.PositiveIntegerField()),
                ('comment', models.TextField(max_length=250)),
                ('allowed_to_fail', models.BooleanField(default=False)),
                ('valid', models.BooleanField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contenttypes.ContentType')),
                ('method', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='datavalidation.Validator')),
            ],
            options={
                'unique_together': {('content_type', 'object_pk', 'method')},
                'index_together': {('content_type', 'object_pk', 'method')},
            },
        ),
    ]
