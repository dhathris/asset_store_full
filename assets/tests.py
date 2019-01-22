from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from rest_framework.renderers import JSONRenderer
from .models import Asset, AssetDetail
from .serializers import AssetSerializer
import json

# Create your tests here.


class BaseTest(APITestCase):
    client = APIClient()
    content_type = "application/json"

    @staticmethod
    def create_asset(name="", type="", aclass=""):
        if name != "" and type != "" and aclass != "":
            Asset.objects.create(asset_name=name, asset_type=type, asset_class=aclass)

    def setUp(self):
        # add the test data
        self.create_asset("Dove1", "satellite", "dove")
        self.create_asset("SkySat1", "satellite", "skysat")
        self.create_asset("RapidEye1", "satellite", "rapideye")
        self.create_asset("Dish1", "antenna", "dish")
        self.create_asset("Yagi1", "antenna", "yagi")


class GetAllAssetsTest(BaseTest):

    def test_get_all_assets(self):
        """
        This test makes sure all Assets from database are returned in
        the GET ALL API response
        """
        # hit the API endpoint
        response = self.client.get(reverse("assets"))

        # fetch the data from db
        expected = Asset.objects.all()
        serialized = AssetSerializer(expected, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data["assets"], serialized.data)

    def process_request_with_filters(self, query_params):
        # hit the API endpoint
        response = self.client.get(reverse("assets"), kwargs=query_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        all = Asset.objects.all()
        filtered = []
        if 'asset_class' in query_params:
            filtered = all.filter(asset_class=query_params['asset_class'])
        if 'asset_type' in query_params:
            filtered = [filtered.append(x) for x in all.filter(asset_type=query_params['asset_type'])]
        if len(filtered) == 0:
            filtered = all
        serialized = AssetSerializer(filtered, many=True)

        self.assertEquals(response.data["assets"], serialized.data)

    def test_get_all_assets_with_filters(self):
        """
        This test additionally filters requests with query parameters asset_name and/or asset_type
        :return:
        """
        self.process_request_with_filters({'asset_class': 'satellite'})
        self.process_request_with_filters({'asset_class': 'antenna'})
        self.process_request_with_filters({'asset_type': 'dove'})
        self.process_request_with_filters({'asset_type': 'skysat'})
        self.process_request_with_filters({'asset_type': 'rapideye'})
        self.process_request_with_filters({'asset_type': 'dish'})
        self.process_request_with_filters({'asset_type': 'yagi'})
        self.process_request_with_filters({'asset_class': 'satellite', 'asset_type': 'dove'})
        self.process_request_with_filters({'asset_class': 'satellite', 'asset_type': 'skysat'})
        self.process_request_with_filters({'asset_class': 'satellite', 'asset_type': 'rapideye'})
        self.process_request_with_filters({'asset_class': 'antenna', 'asset_type': 'dish'})
        self.process_request_with_filters({'asset_class': 'antenna', 'asset_type': 'yagi'})

    def test_get_all_assets_with_filters_negative_cases(self):
        """
        This test attempts to filter GET results on invalid parameters for asset_class and asset_type
        :return:
        """
        self.process_request_with_filters({'asset_class': 'abc123'})
        self.process_request_with_filters({'asset_type': 'abc123'})
        self.process_request_with_filters({'asset_class': 'abc123', 'asset_type': 'xyz123'})


class GetAnAssetTest(BaseTest):

    def verify_get_an_asset(self, name):
        """
        This method makes sure a single asset referenced in the path of the GET
        request is returned correctly, when it exists in the database
        """
        response = self.client.get(reverse("asset", args=[name]))
        expected = Asset.objects.get(asset_name=name)
        serialized = AssetSerializer(expected)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.data['asset_name'], serialized.data['asset_name'])

    def test_get_an_asset(self):
        self.verify_get_an_asset("Dove1")
        self.verify_get_an_asset("SkySat1")
        self.verify_get_an_asset("RapidEye1")
        self.verify_get_an_asset("Dish1")
        self.verify_get_an_asset("Yagi1")

    def test_get_an_asset_with_details(self):
        payloads = {"Dish1": {"diameter": 35.5, "radome": True},
                   "Yagi1": {"gain": 12.45}}
        for key, payload in payloads.items():
            resp = self.client.put(reverse("asset", kwargs={"asset_name": key}), json.dumps(payload), format=None,
                               content_type=self.content_type)
            self.assertEqual(status.HTTP_200_OK, resp.status_code)
            resp = self.client.get(reverse("asset", kwargs={"asset_name": key}))
            self.assertEqual(status.HTTP_200_OK, resp.status_code)
            for prop, value in payload.items():
                self.assertEqual(value, resp.data[prop])

    def test_get_an_asset_negative_cases(self):
        negative_cases = ["Sky130", "()123abc", "(^abc123)", "Do", "Dove1234Dove1234Dove1234Dove1234Dove1234Dove1234Dove1234Dove1234Dove"]

        for asset in negative_cases:
            response = self.client.get("/api/v1/assets/"+asset)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UpdateAnAssetTest(BaseTest):

    def setUp(self):
        super(UpdateAnAssetTest, self).setUp()
        self.create_asset("Dish9087", "antenna", "dish")
        self.create_asset("Yagi9087", "antenna", "yagi")

    def test_update_an_asset(self):
        payloads = {"Dish9087": {"diameter": 35.5, "radome": True},
                   "Yagi9087": {"gain": 12.45}}
        for key, payload in payloads.items():
            resp = self.client.put(reverse("asset", kwargs={"asset_name": key}), json.dumps(payload), format=None,
                                   content_type=self.content_type)
            self.assertEqual(status.HTTP_200_OK, resp.status_code, resp.data)
            asset = Asset.objects.get(asset_name=key)
            asset_details = AssetDetail.objects.filter(asset_id=asset.id)
            self.assertIsNotNone(asset_details)
            for asset_detail in asset_details:
                self.assertEqual(str(payload.get(asset_detail.asset_detail_name)), asset_detail.asset_detail_value)

    def test_upload_an_asset_negative_cases(self):
        payloads = {"Dish9087": {"diametertest": 35.5, "radome": True, "asset_type": "satellite",
                                 "asset_class": "yagi"},
                   "Yagi9087": {"gaintest": 12.45}}
        errors = {"Dish9087": ["diametertest is either not a valid property or not allowed to be updated for a dish",
                               "asset_type is either not a valid property or not allowed to be updated for a dish",
                               "asset_class is either not a valid property or not allowed to be updated for a dish"],
                  "Yagi9087": ["gaintest is either not a valid property or not allowed to be updated for a yagi"]}
        props = {"Dish9087": ["diametertest", "asset_type", "asset_class"],
                 "Yagi9087": ["gaintest"]}
        for key, payload in payloads.items():
            resp = self.client.put(reverse("asset", kwargs={"asset_name": key}), json.dumps(payload), format=None,
                                   content_type=self.content_type)
            self.assertEqual(status.HTTP_400_BAD_REQUEST, resp.status_code)
            self.assertIsNotNone(resp.data.get('errors'))
            self.assertEqual(len(errors.get(key)), len(resp.data.get('errors')))
            index = 0
            for error in errors.get(key):
                self.assertEqual(error, resp.data.get('errors').get(props.get(key)[index]))
                index = index + 1


class CreateAssetsTest(BaseTest):
    post_headers = {"X-User": "admin"}

    def test_post_an_asset(self):
        single_asset = {"asset_name": "SkySat123", "asset_type": "satellite", "asset_class": "skysat"}
        payload = {"assets": [single_asset]}

        response = self.client.post(reverse("assets"), JSONRenderer().render(payload), format=None,
                                    content_type=self.content_type, HTTP_X_USER=self.post_headers.get('X-User'))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = Asset.objects.get(asset_name=single_asset['asset_name'])
        serialized = AssetSerializer(expected)

        self.assertEqual(single_asset['asset_name'], serialized.data['asset_name'])
        self.assertEqual(single_asset['asset_type'], serialized.data['asset_type'])
        self.assertEqual(single_asset['asset_class'], serialized.data['asset_class'])

    def verify_post_an_asset_with_errors(self, payload, name, messages):
        response = self.client.post(reverse("assets"), JSONRenderer().render(payload), format=None,
                                    content_type=self.content_type, HTTP_X_USER=self.post_headers.get('X-User'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error_message = response.data['assets'][0]
        self.assertEqual(name, error_message['asset_name'])
        self.assertEqual(messages, error_message['errors'])

    def test_post_an_asset_negative_cases(self):
        assets = {"name_error": {"asset_name": "(^abc123)", "asset_type": "satellite", "asset_class": "skysat"},
                  "type_error": {"asset_name": "SkySat123", "asset_type": "abcd1234", "asset_class": "skysat"},
                  "class_error": {"asset_name": "SkySat123", "asset_type": "satellite", "asset_class": "dish"},
                  "exists_error": {"asset_name": "SkySat1", "asset_type": "satellite", "asset_class": "skysat"}}
        error_messages = {"name_error": ["asset_name is not formatted correctly"],
                          "type_error": ['"abcd1234" is not a valid choice. for asset_type'],
                          "class_error": ["asset_class is not valid"],
                          "exists_error": ["Asset already exists in the asset store, it cannot be updated using a POST request"]}
        for key, value in assets.items():
            payload = {"assets": [value]}
            self.verify_post_an_asset_with_errors(payload, value['asset_name'], error_messages[key])
            
    def test_post_multiple_assets(self):
        assets = []
        assets.append({"asset_name": "SkySat678", "asset_type": "satellite", "asset_class": "skysat"})
        assets.append({"asset_name": "Dove678", "asset_type": "satellite", "asset_class": "dove"})
        assets.append({"asset_name": "RapidEye678", "asset_type": "satellite", "asset_class": "rapideye"})
        assets.append({"asset_name": "Dish678", "asset_type": "antenna", "asset_class": "dish"})
        assets.append({"asset_name": "Yagi678", "asset_type": "antenna", "asset_class": "yagi"})

        payload = {"assets": assets}
        response = self.client.post(reverse("assets"), JSONRenderer().render(payload), format=None,
                                    content_type=self.content_type, HTTP_X_USER=self.post_headers.get('X-User'))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Validate that the assets exist in the database
        for asset in assets:
            try:
                Asset.objects.get(asset_name=asset['asset_name'])
            except Asset.DoesNotExist:
                self.assertFalse(True, asset['asset_name'] + " is not stored in asset store")

    def test_post_multiple_assets_errors(self):
        assets = [{"asset_name": "(^abc123)", "asset_type": "satellite", "asset_class": "skysat"},
                  {"asset_name": "SkySat123", "asset_type": "abcd1234", "asset_class": "skysat"},
                  {"asset_name": "SkySat123", "asset_type": "satellite", "asset_class": "dish"},
                  {"asset_name": "SkySat1", "asset_type": "satellite", "asset_class": "skysat"},
                  {"asset_name": "SkySat1765", "asset_type": "satellite", "asset_class": "skysat"}]
        error_messages = [["asset_name is not formatted correctly"],
                          ['"abcd1234" is not a valid choice. for asset_type'],
                          ["asset_class is not valid"],
                          ["Asset already exists in the asset store, it cannot be updated using a POST request"],
                          ["Asset is valid and does not yet exist in the asset store"]]
        payload = {"assets": assets}
        response = self.client.post(reverse("assets"), JSONRenderer().render(payload), format=None,
                                    content_type=self.content_type, HTTP_X_USER=self.post_headers.get('X-User'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data['assets']
        index = 0
        for asset in assets:
            self.assertEqual(asset['asset_name'], errors[index]['asset_name'])
            self.assertEqual(error_messages[index], errors[index]['errors'])
            index = index + 1

    def test_post_with_user_header_missing(self):
        single_asset = {"asset_name": "SkySat123", "asset_type": "satellite", "asset_class": "skysat"}
        payload = {"assets": [single_asset]}

        response = self.client.post(reverse("assets"), JSONRenderer().render(payload), format=None,
                                    content_type=self.content_type)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        self.assertEqual("Only user 'admin' is allowed to create asset(s). "
                         + "X-User header with value 'admin' is required!", response.data)

    def test_post_with_non_admin_user_header(self):
        single_asset = {"asset_name": "SkySat123", "asset_type": "satellite", "asset_class": "skysat"}
        payload = {"assets": [single_asset]}

        response = self.client.post(reverse("assets"), JSONRenderer().render(payload), format=None,
                                    content_type=self.content_type, HTTP_X_USER="nonadmdin")
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        self.assertEqual("Only user 'admin' is allowed to create asset(s). "
                         + "X-User header with value 'admin' is required!", response.data)
