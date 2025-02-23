from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.template import RequestContext
from django.apps import apps
import hmac, base64, hashlib, binascii, os
import shopify

from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.sessions.backends.signed_cookies import SessionStore
import jwt  # PyJWT to decode session tokens

def _new_session(shop_url):
    api_version = apps.get_app_config('shopify_app').SHOPIFY_API_VERSION
    return shopify.Session(shop_url, api_version)

# Ask user for their ${shop}.myshopify.com address
def login(request):
    # If the ${shop}.myshopify.com address is already provided in the URL,
    # just skip to authenticate
    if request.GET.get('shop'):
        return authenticate(request)
    return render(request, 'shopify_app/login.html', {})

def authenticate(request):
    shop_url = request.GET.get('shop', request.POST.get('shop')).strip()
    if not shop_url:
        messages.error(request, "A shop param is required")
        return redirect(reverse(login))
    scope = apps.get_app_config('shopify_app').SHOPIFY_API_SCOPE
    redirect_uri = request.build_absolute_uri(reverse(finalize))
    state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
    request.session['shopify_oauth_state_param'] = state
    permission_url = _new_session(shop_url).create_permission_url(scope, redirect_uri, state)
    return redirect(permission_url)


def finalize(request):
    """Handles Shopify OAuth finalization and session setup"""
    params = request.GET
    shop_url = params.get("shop")

    # Step 1: Validate and retrieve access token
    shopify_session = shopify.Session(shop_url, settings.SHOPIFY_API_VERSION)
    token = shopify_session.request_token(params)

    # Step 2: Store authentication details in session
    request.session["shopify"] = {
        "shop_url": shop_url,
        "access_token": token
    }
    print("Session after finalize:", request.session.get("shopify"))

    # Step 3: Redirect to home page inside Shopify (to prevent infinite loop)
    return redirect("/")



def logout(request):
    request.session.pop('shopify', None)
    messages.info(request, "Successfully logged out.")
    return redirect(reverse(login))
