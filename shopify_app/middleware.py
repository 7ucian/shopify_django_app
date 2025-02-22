from django.apps import apps
from django.http import HttpResponseRedirect

from django.shortcuts import redirect
from urllib.parse import urlencode
import jwt  # PyJWT to decode Shopify session tokens
from django.urls import reverse
import shopify
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class ConfigurationError(BaseException):
    pass

class LoginProtection(MiddlewareMixin):
    async_mode = False  # ✅ Fix for Django middleware compatibility

    def __init__(self, get_response):
        super().__init__(get_response)
        self.api_key = apps.get_app_config('shopify_app').SHOPIFY_API_KEY
        self.api_secret = apps.get_app_config('shopify_app').SHOPIFY_API_SECRET
        if not self.api_key or not self.api_secret:
            raise ConfigurationError("SHOPIFY_API_KEY and SHOPIFY_API_SECRET must be set in ShopifyAppConfig")
        shopify.Session.setup(api_key=self.api_key, secret=self.api_secret)

    def process_request(self, request):
        """Ensure user is authenticated using Shopify session token (not cookies)."""

        # ✅ Step 1: If already authenticated, allow request
        if hasattr(request, "session") and "shopify" in request.session:
            session_data = request.session["shopify"]
            if "access_token" in session_data:
                shop_url = session_data["shop_url"]
                api_version = apps.get_app_config("shopify_app").SHOPIFY_API_VERSION
                shopify_session = shopify.Session(shop_url, api_version)
                shopify_session.token = session_data["access_token"]
                shopify.ShopifyResource.activate_session(shopify_session)
                return  # ✅ Allow request to proceed

        # ✅ Step 2: If coming from `/shopify/finalize/`, do NOT redirect back to authenticate
        if request.path.startswith("/shopify/finalize/"):
            return  # Stop middleware from forcing another redirect

        # ✅ Step 3: If no session, redirect to authentication
        shop = request.GET.get("shop")
        if shop and not request.path.startswith("/shopify/authenticate"):
            return redirect(f"/shopify/authenticate/?shop={shop}")

    def process_response(self, request, response):
        """Clears the Shopify session after response is processed."""
        shopify.ShopifyResource.clear_session()
        return response