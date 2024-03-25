import base64
import binascii
import collections
import hashlib
import hmac
import secrets
import string
import time
from urllib.parse import quote
from urllib.parse import urlencode

from oauthlib import oauth1

from . import constants

random_string = lambda length: "".join(
    secrets.choice(string.ascii_lowercase + string.ascii_lowercase)
    for _ in range(length)
)

escape = lambda s: quote(s, safe="~")


def generate_nonce():
    random_bytes = b"\x00" + secrets.token_bytes(32) + b"\x00"
    b64_encoded = base64.b64encode(random_bytes)

    return b64_encoded.decode()


def stringify_parameters(parameters):
    output = ""
    ordered_parameters = collections.OrderedDict(sorted(parameters.items()))

    counter = 1
    for k, v in ordered_parameters.items():
        output += escape(str(k)) + "=" + escape(str(v))
        if counter < len(ordered_parameters):
            output += "&"
            counter += 1

    return output


def SignatureString(data, url, method, payload):
    z = {
        **data,
        **payload,
    }

    signature_base_string = (
        method + "&" + escape(url) + "&" + escape(stringify_parameters(z))
    )

    return signature_base_string


def SigningKey(secret):
    signingkeys = escape("GgDYlkSvaPxGxC4X8liwpUoqKwwr3lCADbz8A7ADU") + "&"
    signingkeys += escape(secret)

    return signingkeys


def calculate_signature(signing_key, signature_base_string):
    """Calculate the signature using SHA1"""
    hashed = hmac.new(
        signing_key.encode("utf-8"), signature_base_string.encode("utf-8"), hashlib.sha1
    )

    sig = binascii.b2a_base64(hashed.digest())[:-1]

    return escape(sig)


def getAuth(method, url, secret, token, params):
    client = oauth1.Client(
        "IQKbtAYlXLripLGPWd0HUA",
        client_secret="GgDYlkSvaPxGxC4X8liwpUoqKwwr3lCADbz8A7ADU",
        resource_owner_key=token,
        resource_owner_secret=secret,
        signature_method=oauth1.SIGNATURE_HMAC_SHA1,
    )

    if params is None:
        params = constants.GENERAL_PARAMS
        enc = urlencode(params)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        _, headers, _ = client.sign(url, http_method=method, headers=headers, body=enc)
        return headers["Authorization"]
    if params == "NO_VALUE":
        _, headers, _ = client.sign(url, http_method=method)
        return headers["Authorization"]
    enc = urlencode(params)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    _, headers, _ = client.sign(url, http_method=method, headers=headers, body=enc)
    return headers["Authorization"]


def getAuth2(method, url, secret, token, params):
    auths = {
        "oauth_nonce": random_string(64),
        "oauth_timestamp": str(int(time.time())),
        "oauth_consumer_key": "IQKbtAYlXLripLGPWd0HUA",
        "oauth_token": token,
        "oauth_version": "1.0",
        "oauth_signature_method": "HMAC-SHA1",
    }

    if params is None:
        params = constants.GENERAL_PARAMS
    signature_string = SignatureString(auths, url, method, params)
    signing_key = SigningKey(secret)

    auths["oauth_signature"] = calculate_signature(signing_key, signature_string)

    ordered_parameters = {}
    ordered_parameters = collections.OrderedDict(sorted(auths.items()))
    auth_header = ('%s="%s"' % (k, v) for k, v in ordered_parameters.items())

    val = "OAuth " + ", ".join(auth_header)

    return val
