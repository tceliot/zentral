# Generated by Django 4.2.11 on 2024-05-21 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mdm', '0077_alter_scepconfig_challenge_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='depenrollment',
            name='display_name',
            field=models.CharField(default='Zentral MDM',
                                   help_text='Name displayed in the device settings', max_length=128),
        ),
        migrations.AddField(
            model_name='otaenrollment',
            name='display_name',
            field=models.CharField(default='Zentral MDM',
                                   help_text='Name displayed in the device settings', max_length=128),
        ),
        migrations.AddField(
            model_name='userenrollment',
            name='display_name',
            field=models.CharField(default='Zentral MDM',
                                   help_text='Name displayed in the device settings', max_length=128),
        ),
    ]