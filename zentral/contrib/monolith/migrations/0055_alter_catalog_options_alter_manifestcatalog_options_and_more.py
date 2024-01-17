# Generated by Django 4.2.8 on 2024-01-17 13:59

from django.db import migrations, models
import django.db.models.deletion


def create_repository(apps, schema_editor):
    try:
        from zentral.conf import settings
        config_repo = settings["apps"]["zentral.contrib.monolith"]["munki_repository"]
    except Exception:
        return
    try:
        from zentral.contrib.monolith.repository_backends import RepositoryBackend
        config_repo = config_repo or {}
        if config_repo.get("backend") == "zentral.contrib.monolith.repository_backends.s3":
            backend = RepositoryBackend.S3
            backend_kwargs = {}
            for db_a, cfg_a in (("bucket", "bucket"),
                                ("region_name", "region_name"),
                                ("prefix", "prefix"),
                                ("access_key_id", "aws_access_key_id"),
                                ("secret_access_key", "aws_secret_access_key"),
                                ("assume_role_arn", "assume_role_arn"),
                                ("signature_version", "signature_version"),
                                ("endpoint_url", "endpoint_url")):
                val = config_repo.get(cfg_a)
                if val is not None:
                    backend_kwargs[db_a] = val
            cloudfront_cfg = config_repo.get("cloudfront")
            if cloudfront_cfg:
                for db_a, cfg_a in (("cloudfront_domain", "domain"),
                                    ("cloudfront_key_id", "key_id"),
                                    ("cloudfront_privkey_pem", "privkey_pem")):
                    val = cloudfront_cfg.get(cfg_a)
                    if val is not None:
                        backend_kwargs[db_a] = val
        else:
            backend = RepositoryBackend.VIRTUAL
            backend_kwargs = {}
        from zentral.contrib.monolith.models import Repository
        repository = Repository.objects.create(
            name="Default",
            meta_business_unit=None,
            backend=backend,
            backend_kwargs={},
        )
        repository.set_backend_kwargs(backend_kwargs)
        repository.save()
        Catalog = apps.get_model("monolith", "Catalog")
        Catalog.objects.update(repository=repository)
        PkgInfoCategory = apps.get_model("monolith", "PkgInfoCategory")
        PkgInfoCategory.objects.update(repository=repository)
        PkgInfo = apps.get_model("monolith", "PkgInfo")
        PkgInfo.objects.update(repository=repository)
    except Exception:
        return


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0077_file_signing_id'),
        ('monolith', '0054_auto_20230317_0921'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='manifestcatalog',
            options={'ordering': ('catalog__name',)},
        ),
        migrations.AlterField(
            model_name='catalog',
            name='name',
            field=models.CharField(max_length=256),
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True)),
                ('backend', models.CharField(choices=[('S3', 'Amazon S3'), ('VIRTUAL', 'Virtual')], max_length=32)),
                ('backend_kwargs', models.JSONField(editable=False)),
                ('icon_hashes', models.JSONField(default=dict, editable=False)),
                ('client_resources', models.JSONField(default=list, editable=False)),
                ('last_synced_at', models.DateTimeField(editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('meta_business_unit', models.ForeignKey(blank=True, null=True,
                                                         on_delete=django.db.models.deletion.SET_NULL,
                                                         to='inventory.metabusinessunit')),
            ],
        ),
        migrations.AlterModelOptions(
            name='repository',
            options={'ordering': ('name',), 'permissions': [('sync_repository', 'Can sync repository')]},
        ),
        migrations.AddField(
            model_name='catalog',
            name='repository',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='monolith.repository'),
        ),
        migrations.AlterField(
            model_name='catalog',
            name='archived_at',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AlterModelOptions(
            name='catalog',
            options={'ordering': ('-archived_at', 'repository__name', 'name', 'pk')},
        ),
        migrations.AddField(
            model_name='pkginfo',
            name='repository',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='monolith.repository'),
        ),
        migrations.AddField(
            model_name='pkginfocategory',
            name='repository',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='monolith.repository'),
        ),
        migrations.AlterUniqueTogether(
            name='catalog',
            unique_together={('repository', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='pkginfocategory',
            unique_together={('repository', 'name')},
        ),
        migrations.RemoveField(
            model_name='catalog',
            name='priority',
        ),
        migrations.RunPython(create_repository),
        migrations.AlterField(
            model_name='catalog',
            name='repository',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='monolith.repository'),
        ),
        migrations.AlterField(
            model_name='pkginfo',
            name='repository',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='monolith.repository'),
        ),
        migrations.AlterField(
            model_name='pkginfocategory',
            name='repository',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='monolith.repository'),
        ),
    ]
