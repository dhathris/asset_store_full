from django.db import models
import json, types

# Create your models here.


class Asset(models.Model):
    # asset name
    asset_name = models.CharField(max_length=64, null=False)
    # asset type
    asset_type = models.CharField(max_length=64, null=False)
    # asset class
    asset_class = models.CharField(max_length=64, null=False)

    def __str__(self):
        data = {}
        data['asset_name'] = self.asset_name
        data['asset_type'] = self.asset_type
        data['asset_class'] = self.asset_class
        return json.dumps(data)
        # return "Asset(asset_name={}, asset_type={}, asset_class={})".format(self.asset_name, self.asset_type, self.asset_class)

    @staticmethod
    def convert_dict_to_asset(indict):
        return Asset(asset_name=indict['asset_name'], asset_type=indict['asset_type'],
                     asset_class=indict['asset_class'])


TYPES = ["satellite", "antenna"]
CLASSES = ["dove", "skysat", "rapideye", "dish", "yagi"]
SAT_CLASSES = CLASSES[0:3]
ANT_CLASSES = CLASSES[3:5]
DATA_TYPES = {"float": float, "bool": bool}

class AssetDetail(models.Model):
    # Foreign key
    asset_id = models.ForeignKey(Asset, on_delete=models.CASCADE)
    # detail name
    asset_detail_name = models.CharField(max_length=128, null=False)
    # detail value
    asset_detail_value = models.CharField(max_length=256, null=False)

    @staticmethod
    def convert_dict_to_asset_details(indict):
        return AssetDetail(asset_id=indict['asset_id'], asset_detail_name=indict['asset_detail_name'],
                            asset_detail_value=indict['asset_detail_value'])


class AssetDetailMeta(models.Model):
    # Asset class
    asset_class = models.CharField(max_length=64, null=False)
    # Asset detail name
    asset_detail_name = models.CharField(max_length=128, null=False)
    # Asset detail type
    asset_detail_type = models.CharField(max_length=128, null=False)

