from django.http import Http404
from rest_framework.parsers import JSONParser
from rest_framework import generics
from rest_framework.views import APIView, status
from rest_framework.response import Response
import re, types
from .models import Asset, AssetDetail, AssetDetailMeta, TYPES, SAT_CLASSES, ANT_CLASSES, DATA_TYPES
from .serializers import AssetSerializer

# Create your views here.


class ListAssetsView(generics.ListAPIView):
    """
    Provides GET method handler
    """
    def get_queryset(self):
        queryset = Asset.objects.all()
        a_class = self.request.query_params.get('asset_class', None)
        a_type = self.request.query_params.get('asset_type', None)
        result = []
        if a_class is not None:
            result = queryset.filter(asset_class=a_class)
        if a_type is not None:
            if len(result) == 0:
                result = queryset.filter(asset_type=a_type)
            else:
                result = [result.append(x) for x in queryset.filter(asset_type=a_type)]
        if len(result) == 0:
            result = queryset
        return result

    def get(self, request, *args, **kwargs):
        assets = self.get_queryset()
        serializer = AssetSerializer(assets, many=True)
        resp = {"assets": serializer.data}
        return Response(resp, status=status.HTTP_200_OK)


class ListAssetView(generics.ListAPIView):
    """
    Provides GET method handler for a single asset
    """
    def get_object(self, pk):
        try:
            return Asset.objects.get(asset_name=pk)
        except Asset.DoesNotExist:
            raise Http404

    @staticmethod
    def get_asset_details(pk):
        try:
            return AssetDetail.objects.filter(asset_id=pk)
        except AssetDetail.DoesNotExist:
            print("No asset details found for {}".format(pk))

    def get(self, request, asset_name, format=None):
        asset = self.get_object(asset_name)
        serializer = AssetSerializer(asset)
        # Populate the details
        asset_details = self.get_asset_details(asset.id)
        if asset_details is not None:
            resp = {}
            for key, value in serializer.data.items():
                    resp[key] = value
            for asset_detail in asset_details:
                try:
                    resp[asset_detail.asset_detail_name] = float(asset_detail.asset_detail_value)
                except ValueError:
                    if bool(asset_detail.asset_detail_value) is True:
                        resp[asset_detail.asset_detail_name] = bool(asset_detail.asset_detail_value)
                    else:
                        resp[asset_detail.asset_detail_name] = asset_detail.asset_detail_value
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(resp, status=status.HTTP_200_OK)
        # return Response(asset, status=status.HTTP_200_OK)


class CreateAssetsView(generics.CreateAPIView):
    """
    Provides POST method handler
    """
    @staticmethod
    def validate_asset(asset):
        match = re.search(r'^([\w\-]{4,64})$', asset['asset_name'])

        errors = []
        if match is None:
            errors.append("asset_name is not formatted correctly")
        else:
            name = "".join(asset['asset_name'])
            if name.startswith("_") or name.startswith("-"):
                errors.append("asset_name cannot start with either _ or -")
        if asset['asset_type'] == TYPES[0]:
            if asset['asset_class'] not in SAT_CLASSES:
                errors.append("asset_class is not valid")
        elif asset['asset_class'] not in ANT_CLASSES:
            return errors.append("asset_class is not valid")
        try:
            asset = Asset.objects.get(asset_name=asset['asset_name'])
            if asset is not None:
                errors.append("Asset already exists in the asset store, it cannot be updated using a POST request")
        except Asset.DoesNotExist:
            # Ignore the exception
            print("")
        return errors

    def post(self, request, *args, **kwargs):
        x_user = request.META.get('HTTP_X_USER')
        if x_user is None or x_user != "admin":
            return Response("Only user 'admin' is allowed to create asset(s)."
                            + " X-User header with value 'admin' is required!",status=status.HTTP_406_NOT_ACCEPTABLE)

        data = JSONParser().parse(request)

        assets = data['assets']
        messages = []
        error_flag = False
        for asset in assets:
            message = {}
            message['asset_name'] = asset['asset_name']
            message['errors'] = []
            serializer = AssetSerializer(data=asset)
            if not serializer.is_valid():
                for key, value in serializer.errors.items():
                    message['errors'].append(value[0]+" for "+key)
                error_flag = True
            result = self.validate_asset(asset)
            if result is not None and len(result) != 0:
                [message['errors'].append(x) for x in result]
                error_flag = True
            elif len(message['errors']) == 0:
                message['errors'].append("Asset is valid and does not yet exist in the asset store")
            messages.append(message)
        if error_flag:
            return Response(data={"assets": messages}, status=status.HTTP_400_BAD_REQUEST)
        """
        Perform a bulk update here
        """
        Asset.objects.bulk_create([Asset.convert_dict_to_asset(x) for x in assets])
        return Response(status=status.HTTP_201_CREATED)


class CreateAssetView(generics.CreateAPIView):
    """
    Provides a handler for single asset creation using POST
    """
    def post(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class UpdateAssetsView(generics.UpdateAPIView):
    """
    Provides PUT method handler for bulk update
    """
    def put(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class UpdateAssetView(generics.UpdateAPIView):
    """
    Provides PUT method handler for single asset details update
    """
    def get_object(self, pk):
        try:
            return Asset.objects.get(asset_name=pk)
        except Asset.DoesNotExist:
            raise Http404

    def validate_details(self, asset_details_meta, data, asset_class):
        dtypes = {}
        errors = {}
        if asset_details_meta is not None:
            for asset_detail_meta in asset_details_meta:
                dtypes[asset_detail_meta.asset_detail_name] = asset_detail_meta.asset_detail_type
        else:
            for detail in data.keys():
                errors[detail] = "Property is NOT allowed to be set/update for asset_class {}".format(asset_class)
            return errors

        for detail, value in data.items():
            if dtypes.get(detail) is None:
                errors[detail] = "{} is either not a valid property or not allowed to be updated for a {}".format(detail, asset_class)
            else:
                dtype = type(value).__name__
                if dtype != dtypes.get(detail):
                    errors[detail] = "Invalid data type. Expecting a {}".format(dtypes.get(detail))
        return errors

    def check_for_existence(self, pk, asset_detail_name):
        try:
            asset_detail = AssetDetail.objects.get(asset_id=pk, asset_detail_name=asset_detail_name)
            return asset_detail
        except AssetDetail.DoesNotExist:
            return None

    def put(self, request, asset_name, **kwargs):
        data = JSONParser().parse(request)

        if data is None or len(data) == 0:
            return Response("Request body must contain asset details to set on the asset",
                            status=status.HTTP_400_BAD_REQUEST)
        asset = self.get_object(asset_name)
        asset_details_meta = AssetDetailMeta.objects.filter(asset_class=asset.asset_class)
        errors = self.validate_details(asset_details_meta, data, asset.asset_class)
        if len(errors) > 0:
            return Response(data={"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        asset_details_to_create = []
        for detail, value in data.items():
            asset_detail = self.check_for_existence(asset.id, detail)
            if asset_detail is None:
                indict = {"asset_id": asset, "asset_detail_name": detail, "asset_detail_value": value}
                asset_details_to_create.append(AssetDetail.convert_dict_to_asset_details(indict))
            else:
                asset_detail.asset_detail_value = data.get(detail)
                asset_detail.save()
        if len(asset_details_to_create) > 0:
            AssetDetail.objects.bulk_create(asset_details_to_create)

        return Response(status=status.HTTP_200_OK)


class DeleteAssetsView(generics.DestroyAPIView):
    """
    This is a DELETE method handler for bulk asset delete
    """
    def delete(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class DeleteAssetView(generics.DestroyAPIView):
    """
    This is a DELETE method handler for a single asset delete
    """
    def delete(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class BaseView(APIView):
    """
    Base view class for routing requests to different view classes based on HTTP Methods for the same url
    """
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(self, 'VIEWS_BY_METHOD'):
            raise Exception('VIEWS_BY_METHOD static dictionary variable must be defined on a BaseView class!')
        if request.method in self.VIEWS_BY_METHOD:
            return self.VIEWS_BY_METHOD[request.method]()(request, *args, **kwargs)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class AssetsViewRouter(BaseView):
    VIEWS_BY_METHOD = {
        'GET': ListAssetsView.as_view,
        'POST': CreateAssetsView.as_view,
        'PUT': UpdateAssetsView.as_view,
        'DELETE': DeleteAssetsView.as_view
    }


class AssetViewRouter(BaseView):
    VIEWS_BY_METHOD = {
        'GET': ListAssetView.as_view,
        'POST': CreateAssetView.as_view,
        'PUT': UpdateAssetView.as_view,
        'DELETE': DeleteAssetView.as_view
    }
