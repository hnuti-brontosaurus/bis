import re
import time
from functools import lru_cache
from typing import List, Union

import requests
from django.conf import settings
from requests.adapters import HTTPAdapter
from rest_framework.utils import json
from simplejson import JSONDecodeError
from urllib3.util import Retry

from ecomail.models import Contact, ContactLog

BASE_URI = "https://api2.ecomailapp.cz/"


def send(contacts: Union[Contact, List[Contact]], method, uri, data=None, params=None):
    if data is None:
        data = {}
    if params is None:
        params = {}
    if not isinstance(contacts, list):
        contacts = [contacts]

    s = requests.Session()
    retries = Retry(total=4, backoff_factor=0.1, allowed_methods=False)
    s.mount(BASE_URI, HTTPAdapter(max_retries=retries))
    response = s.request(
        method,
        BASE_URI + uri,
        json=data,
        params=params,
        headers={"key": settings.ECOMAIL_API_KEY},
    )

    log = (
        f"uri: {uri}\n\n"
        f"status_code: {response.status_code}\n\n"
        f"data: {json.dumps(data)}\n\n"
        f"response: {response.text}\n\n"
        f"reason: {response.reason}\n\n"
    )

    for contact in contacts:
        ContactLog.objects.create(contact=contact, log=log, status=response.status_code)

    try:
        return response.json()
    except JSONDecodeError:
        return {"response": response}


DEFAULT_TEMPLATE_NAME = "Brontosauří informační systém"
TEMPLATE_NAME_PATTERN = re.compile(r"^\s*[\d\w]+\.\s*(.+)$")


@lru_cache(maxsize=64)
def _get_cached_name(template_id: int, time_hash: int) -> str:
    retry_strategy = Retry(total=4, backoff_factor=0.1, allowed_methods=["GET"])
    try:
        with requests.Session() as s:
            s.mount(BASE_URI, HTTPAdapter(max_retries=retry_strategy))

            template_name = (
                s.get(
                    f"{BASE_URI}template/{template_id}",
                    headers={
                        "Accept": "application/json",
                        "key": settings.ECOMAIL_API_KEY,
                    },
                    timeout=10,
                )
                .json()
                .get("name")
            )

            if not template_name or not isinstance(template_name, str):
                return DEFAULT_TEMPLATE_NAME

            match = TEMPLATE_NAME_PATTERN.match(template_name)
            result = match.group(1).strip() if match else template_name.strip()

            return result

    except Exception as e:
        print(f"Error fetching Ecomail template {template_id}: {e}")
        return DEFAULT_TEMPLATE_NAME


def get_name_from_template(template_id: int) -> str:
    """
    Retrieve template name from Ecomail API with 5-minute caching.

    Returns cleaned template name or default on error.

    Examples:
        "  31.Jaký to bylo? " -> "Jaký to bylo?"
        "8a. Konec kvalifikace konzultantů" -> "Konec kvalifikace konzultantů"
        "Beze změny" -> "Beze změny"
    """
    ttl_hash = int(
        time.time() / 300
    )  # changes every 5 minutes, which triggers a change of the cache
    return _get_cached_name(template_id, ttl_hash)
