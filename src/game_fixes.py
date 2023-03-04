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
    }
}


def check_available_fixes(game_id):
    for game in fixes:
        if fixes[game]["guid"] == game_id:
            return Game(game_id, fixes[game]["ProductName"], None, LicenseInfo(LicenseType.SinglePurchase, None))
    return None
