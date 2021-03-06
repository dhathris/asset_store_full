# Generated by Django 2.1.4 on 2019-01-22 05:40

from django.db import migrations, models


def load_asset_detail_meta(apps, schema_editor):
    AssetDetailMeta = apps.get_model("assets", "AssetDetailMeta")
    asset_detail_meta = AssetDetailMeta.objects.all()
    list = []
    if asset_detail_meta is None or len(asset_detail_meta) == 0:
        list.append(AssetDetailMeta(asset_class="dish", asset_detail_name="diameter", asset_detail_type="float"))
        list.append(AssetDetailMeta(asset_class="dish", asset_detail_name="radome", asset_detail_type="bool"))
        list.append(AssetDetailMeta(asset_class="yagi", asset_detail_name="gain", asset_detail_type="float"))

    if len(list) > 0:
        AssetDetailMeta.objects.bulk_create(list)


def delete_asset_detail_meta(apps, schema_editor):
    AssetDetailMeta = apps.get_model("assets", "AssetDetailMeta")
    AssetDetailMeta.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_asset_detail_meta, delete_asset_detail_meta),
    ]
