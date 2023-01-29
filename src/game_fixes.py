from galaxy.api.consts import LicenseType
from galaxy.api.types import Game, LicenseInfo

fixes = {
    "Hook": {
        "guid": "6a8b3aa3-7293-41f0-9e11-12494206e6cb",
        "ProductName": "Hook (2015)"
    }
}


def check_available_fixes(game_id, name):
    for game in fixes:
        if fixes[game]["guid"] == game_id:
            return Game(game_id, "HOOK (2015)", None, LicenseInfo(LicenseType.SinglePurchase, None))
    return None
