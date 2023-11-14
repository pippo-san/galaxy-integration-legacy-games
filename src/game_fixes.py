from galaxy.api.consts import LicenseType
from galaxy.api.types import Game, LicenseInfo

fixes = {
    "Hook": {
        "guid": "6a8b3aa3-7293-41f0-9e11-12494206e6cb",
        "ProductName": "Hook (2015)"
    },
    "The Wild Case": {
        "guid": "fad5198e-5c92-4493-b498-d77dc0ba6111",
        "ProductName": "The Wild Case (2021)"
    },
    "City Legends: Trapped In Mirror CE": {
            "guid": "b8cd4707-bc1d-44c4-90a2-04a07e24640f",
            "ProductName": "City Legends: Trapped In Mirror - Collector's Edition"
    },
    "Road Trip: USA 2 West CE": {
            "guid": "b839c68a-1626-46c7-a378-5625395e95ad",
            "ProductName": "Road Trip: USA 2 West Collector's Edition"
    },
    "Looking for Aliens CE": {
            "guid": "88e3219c-13d1-4fbd-a357-f418a5174305",
            "ProductName": "Looking for Aliens Collector's Edition"
    },
    "Lilas Sky Ark": {
            "guid": "cc584db8-0b8b-460c-bf7a-04c958b50008",
            "ProductName": "Lila's Sky Ark"
    },
    "Unsolved Case: Murderous Script CE": {
            "guid": "988f9e23-8c54-45ad-a236-57637dee5e18",
            "ProductName": "Unsolved Case: Murderous Script - Collector's Edition"
    }
}


def check_available_fixes(game_id):
    for game in fixes:
        if fixes[game]["guid"] == game_id:
            return Game(game_id, fixes[game]["ProductName"], None, LicenseInfo(LicenseType.SinglePurchase, None))
    return None
