# Generated by Django 4.2.13 on 2024-06-08 10:03

from django.db import connection, migrations, models
import django.utils.timezone


def create_all_targets(apps, schema_editor):
    MigrationTarget = apps.get_model("santa", "Target")
    try:
        from zentral.contrib.santa.models import Target
        query, args = Target.objects.search_query()
        from zentral.contrib.santa.forms import test_cdhash, test_sha256, test_signing_id_identifier, test_team_id
    except Exception:
        return
    with connection.cursor() as cursor:
        cursor.execute(query, args)
        cols = [c.name for c in cursor.description]
        while True:
            found_targets = cursor.fetchmany(300)
            if not found_targets:
                break
            new_targets = []
            for found_target in found_targets:
                found_target_d = dict(zip(cols, found_target))
                target_type = found_target_d["target_type"]
                identifier = found_target_d["identifier"]
                identifier = identifier.strip()
                if (
                    (target_type == Target.CDHASH and not test_cdhash(identifier))
                    or (target_type == Target.SIGNING_ID and not test_signing_id_identifier(identifier))
                    or (target_type == Target.TEAM_ID and not test_team_id(identifier))
                    or (target_type in (Target.BUNDLE, Target.BINARY, Target.CERTIFICATE)
                        and not test_sha256(identifier))
                ):
                    print("INCOMPATIBLE IDENTIFIER", target_type, identifier, flush=True)
                else:
                    new_targets.append(
                        MigrationTarget(type=found_target_d["target_type"],
                                        identifier=found_target_d["identifier"])
                    )
            if new_targets:
                MigrationTarget.objects.bulk_create(new_targets, ignore_conflicts=True)


class Migration(migrations.Migration):

    dependencies = [
        ('santa', '0034_enrolledmachine_cdhash_rule_count_alter_target_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='target',
            name='identifier',
            field=models.CharField(max_length=256),
        ),
        migrations.AddField(
            model_name='target',
            name='blocked_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='target',
            name='collected_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='target',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='target',
            name='executed_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='target',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.RunPython(create_all_targets),
    ]