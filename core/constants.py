"""Constants File."""

from typing import Dict

SINGLE_FB_PROFILE_DATA_ITEM: Dict = {
        'id': '',  # Facebook ID
        'friends': [],  # List of SINGLE_FB_FRIEND_DATA_ITEM
        'family': []
}

SINGLE_FB_FRIEND_DATA_ITEM: Dict = {
    'name': '',
    'id': '',
    'path': '',
    'profile_pic': ''
}