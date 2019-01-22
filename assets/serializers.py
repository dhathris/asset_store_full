from rest_framework import serializers
from .models import Asset, TYPES, CLASSES


class AssetSerializer(serializers.Serializer):
    asset_name = serializers.CharField(required=True, allow_blank=False, max_length=64)
    asset_type = serializers.ChoiceField(choices=TYPES, required=True)
    asset_class = serializers.ChoiceField(choices=CLASSES, required=True)

    def create(self, validated_data):
        """
        Create and return a new `Asset` instance, given the validated data.
        """
        return Asset.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Asset` instance, given the validated data.
        """
        instance.asset_name = validated_data.get('asset_name', instance.asset_name)
        instance.asset_type = validated_data.get('asset_type', instance.asset_type)
        instance.asset_class = validated_data.get('asset_class', instance.asset_class)
        instance.save()
        return instance

