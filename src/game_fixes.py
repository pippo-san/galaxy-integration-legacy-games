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
    },
    "Lost Lands: Sand Captivity CE": {
            "guid": "988f9e23-8c54-45ad-a236-57637dee5e18",
            "ProductName": "Lost Lands: Sand Captivity - Collector's Edition (2022)"
    },
    "Rose Riddle: Fairy Tale Detective CE": {
            "guid": "0d5d4f59-bf10-4196-91a5-d6feab41fc52",
            "ProductName": "Rose Riddle: The Fairytale Detective - Collector's Edition"
    },
    "100 Doors: Escape from School": {
            "guid": "9d9b6980-57a3-4e98-bd5f-636e677dcc8a",
            "ProductName": "100 Doors Games: Escape from School"
    },
    "Tearstone: Thieves of the Heart CE": {
            "guid": "3ec9152b-5124-410c-b58d-d1146664bdbf",
            "ProductName": "Tearstone: Thieves of the Heart - Collector's Edition"
    },
    "Gloomy Tales: One Way Ticket CE": {
            "guid": "6b223af5-eccb-48bc-a0a4-b322f79c8f82",
            "ProductName": "Gloomy Tales: One-Way Ticket - Collector's Edition"
    },
    "Christmas Fables: The Magic Snowflake CE": {
            "guid": "8cba2b57-2467-4f10-ab96-a24c5d092f65",
            "ProductName": "Christmas Fables: The Magic Snowflake - Collector's Edition"
    },
    "Royal Romances: Cursed Hearts CE": {
            "guid": "e6670311-ad54-44f3-8df7-0a0767d05c24",
            "ProductName": "Royal Romances: Cursed Hearts - Collector's Edition"
    },
    "New York Mysteries: Power of Art CE": {
            "guid": "c80e616c-fad2-4fcc-b9eb-e4bfee400b25",
            "ProductName": "New York Mysteries: Power of Art - Collector's Edition"
    },
    "Lost and Found Agency 1 CE": {
            "guid": "8cadb07c-f6c6-4bcf-81ba-a24aeaacac34",
            "ProductName": "Lost & Found Agency: Collector's Edition"
    },
    "Big Adventure: Trip to Europe 6 CE": {
            "guid": "e1b9808d-ac11-406a-97ee-7a87ac44d33e",
            "ProductName": "Big Adventure: Trip to Europe 6 - Collector's Edition"
    },
    "Around The World 1: Travel to Brazil CE": {
            "guid": "ae5b8664-b015-4d7e-aa57-3d37e3177015",
            "ProductName": "Around The World: Travel To Brazil - Collector's Edition"
    },
    "Detective Agency: Gray Tie CE": {
            "guid": "69d5c1ad-4287-4159-8de7-2aa32051ba90",
            "ProductName": "Detective Agency Gray Tie: Collector's Edition"
    },
    "Criminal Archives 2: Alphabetic Murders CE": {
            "guid": "15622de4-df3d-4bd1-beb6-84b753f62b1b",
            "ProductName": "Criminal Archives: Alphabetic Murders - Collector's Edition"
    },
    "Word Of The Law Death Mask CE": {
            "guid": "e74335b1-b9ad-4e34-a706-27c733ec1742",
            "ProductName": "Word of the Law: Death Mask - Collector's Edition"
    }
}


def check_available_fixes(game_id):
    for game in fixes:
        if fixes[game]["guid"] == game_id:
            return Game(game_id, fixes[game]["ProductName"], None, LicenseInfo(LicenseType.SinglePurchase, None))
    return None
