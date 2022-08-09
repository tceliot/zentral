# Generated by Django 3.2.14 on 2022-08-09 19:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mdm', '0052_auto_20220804_1741'),
    ]

    operations = [
        migrations.CreateModel(
            name='SoftwareUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform', models.CharField(choices=[('iOS', 'iOS'),
                                                       ('iPadOS', 'iPadOS'),
                                                       ('macOS', 'macOS'),
                                                       ('tvOS', 'tvOS')], max_length=64)),
                ('major', models.PositiveIntegerField()),
                ('minor', models.PositiveIntegerField()),
                ('patch', models.PositiveIntegerField()),
                ('public', models.BooleanField()),
                ('posting_date', models.DateField()),
                ('expiration_date', models.DateField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'unique_together': {('platform', 'major', 'minor', 'patch', 'public')},
            },
        ),
        migrations.CreateModel(
            name='SoftwareUpdateDeviceID',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_id', models.CharField(db_index=True, max_length=32)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('software_update', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                                      to='mdm.softwareupdate')),
            ],
            options={
                'unique_together': {('software_update', 'device_id')},
            },
        ),
    ]
