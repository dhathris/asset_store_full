from django.urls import path, re_path
from .views import AssetsViewRouter, AssetViewRouter


urlpatterns = [
    re_path(r'^$', AssetsViewRouter.as_view(), name="assets"),
    re_path(r'^(?P<asset_name>[\w\-]{4,64})$', AssetViewRouter.as_view(), name="asset")
]