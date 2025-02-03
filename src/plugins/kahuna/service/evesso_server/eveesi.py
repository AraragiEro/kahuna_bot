import requests
from cachetools import TTLCache, cached

# kahuna logger
from ..log_server import logger

def get_request(url, headers=dict(), params=dict()):
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data  # 注意：实际的键可能不同，请参考 ESI 文档
    else:
        logger.error(response.text)
        return None

def verify_token(access_token):
    url = "https://esi.evetech.net/verify/"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data  # 注意：实际的键可能不同，请参考 ESI 文档
    else:
        return None


def get_character_skill_point(access_token, cid):
    url = f"https://esi.evetech.net/latest/characters/{cid}/skills/"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("total_sp")  # modify this line to return the desired data
    else:
        return None


def get_character_wallet(access_token, cid):
    url = f"https://esi.evetech.net/latest/characters/{cid}/wallet/"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data  # modify this line to return the desired data
    else:
        return None


def get_character_portrait(access_token, cid):
    url = f"https://esi.evetech.net/latest/characters/{cid}/portrait/"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data  # modify this line to return the desired data
    else:
        return None

def markets_structures(page, access_token, structure_id):
    url = f"https://esi.evetech.net/latest/markets/structures/{structure_id}/"
    headers = {"Authorization": f"Bearer {access_token}"}
    parament = {"page": page}
    response = requests.get(url, params=parament, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data  # modify this line to return the desired data
    else:
        return None

def markets_region_orders(page: int, region_id: int, type_id: int =None):
    url = f"https://esi.evetech.net/latest/markets/{region_id}/orders/"
    headers = {} # {"Authorization": f"Bearer {access_token}"}
    parament = {"page": page, "type_id": type_id}
    response = requests.get(url, params=parament, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data  # modify this line to return the desired data
    else:
        return None

def characters_character_assets(page: int, access_token: str, character_id: int):
    """

    """
    return get_request(
        f"https://esi.evetech.net/latest/characters/{character_id}/assets/",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"page": page}
    )

CHARACRER_INFO_CACHE = TTLCache(maxsize=10, ttl=1200)
@cached(CHARACRER_INFO_CACHE)
def characters_character(character_id):
    """
# alliance_id - Integer
# birthday -  String (date-time)
# bloodline_id - Integer
# corporation_id - Integer
# description - String
# faction_id - Integer
# gender - String
# name - String
# race_id - Integer
# security_status - Float (min: -10, max: 10)
# title - String
    """
    return get_request(
        f"https://esi.evetech.net/latest/characters/{character_id}/"
    )

def corporations_corporation_assets(page: int, access_token: str, corporation_id: int):
    """
    # is_blueprint_copy - Boolean
    # is_singleton - Boolean
    # item_id - Integer
    # location_flag - String
    # location_id - Integer
    # location_type - String
    # quantity - Integer
    # type_id - Integer
    """
    return get_request(
        f"https://esi.evetech.net/latest/corporations/{corporation_id}/assets/",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"page": page}
    )

def universe_structures_structure(access_token: str, structure_id: int):
    """
    name*	string
    owner_id    int32
    position
        x
        y
        z
    solar_system_id
    type_id
    """
    return get_request(
        f"https://esi.evetech.net/latest/universe/structures/{structure_id}/",
        headers={"Authorization": f"Bearer {access_token}"}
    )

def universe_stations_station(station_id):

    return get_request(
        f"https://esi.evetech.net/latest/universe/stations/{station_id}/"
    )