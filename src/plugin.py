import os
import subprocess
import sys
from pathlib import Path
from time import time
from typing import List, Dict, Union

from galaxy.api.consts import Platform, OSCompatibility, LocalGameState, LicenseType
from galaxy.api.plugin import Plugin, create_and_run_plugin, logger
from galaxy.api.types import Authentication, Game, LocalGame, LicenseInfo, NextStep
from galaxy.proc_tools import process_iter

from client import LegacyGamesClient
from utils import get_uninstall_programs_list, open_launcher_config_file

__version__ = 0.1

# LOCAL_GAMES_TIMEOUT = (1 * 60)
OWNED_GAMES_TIMEOUT = (10 * 60)


class LegacyGamesPlugin(Plugin):
    _owned_games_last_updated = 0
    _local_games_last_updated = 0

    def __init__(self, reader, writer, token):
        super().__init__(
            Platform.Test,
            __version__,
            reader,
            writer,
            token
        )

        self.client_path = LegacyGamesClient()
        self.games = []  # [id, InstDir, GameExe]
        self.owned_games_cache = []  # Game obj
        self.local_games_status = []  # LocalGame obj

        self.config_file = open_launcher_config_file()

        self.username = self.config_file["user"]["profile"]["username"]
        # userId = f["user"]["profile"]["id"]
        self.install_path = self.config_file["settings"]["gameLibraryPath"][0]

    async def authenticate(self, stored_credentials=None):
        logger.info("started authentication")
        user_data = {'username': self.username}
        self.store_credentials(user_data)
        return Authentication("LegacyGames", self.username)

    async def pass_login_credentials(self, step: str, credentials: Dict[str, str], cookies: List[Dict[str, str]]) -> \
            Union[NextStep, Authentication]:
        logger.info("passing cached login credentials")
        logger.info("started authentication")
        user_data = {'username': self.username}
        self.store_credentials(user_data)
        return Authentication("LegacyGames", self.username)

    async def launch_platform_client(self):
        LegacyGamesClient.start_client()

    async def shutdown_platform_client(self):
        self.client_path.stop_client()

    async def get_os_compatibility(self, game_id, context):
        return OSCompatibility.Windows

    def get_giveaway_games(self):
        for game in self.config_file["user"]["giveawayDownloads"]:
            game_id = game["installer_uuid"]
            self.games.append(
                [game_id, None, None]
            )
            game_name = self.find_game_title(game['installer_uuid'])
            logger.info("Game " + game['installer_uuid'] + " added to owned games, with name" + game_name)
            self.owned_games_cache.append(
                Game(
                    game["installer_uuid"],
                    game_name,
                    None,
                    LicenseInfo(LicenseType.SinglePurchase, None)
                )
            )

        return self.owned_games_cache

    def find_game_title(self, installer_uuid):
        for entry in self.config_file["siteData"]["giveawayCatalog"]:
            for game in entry["games"]:
                if game["installer_uuid"] == installer_uuid:
                    print(game["game_name"])
                    return game["game_name"]

    async def get_owned_games(self) -> List[Game]:
        # Clear games list from previously imported games
        self.games.clear()
        self.owned_games_cache.clear()
        self.get_giveaway_games()

        get_games = get_uninstall_programs_list()
        logger.info(get_games)
        if get_games is not None:  # no games found
            for program in get_games:
                logger.info(program)
                if not program['InstDir']:
                    logger.info("program isn't installed")
                    continue

                if not os.path.exists(os.path.abspath(program['InstDir'])):
                    logger.info("program isn't installed")
                    logger.info("nope")
                    continue

                # So we don't have multiple entries of the same game
                self.delete_existent_game_entry(program['id'])

                # games list with install directory and exe
                self.games.append(
                    [program['id'], program['InstDir'], program['GameExe']]
                )

                # Galaxy games list
                logger.info("Game " + program['id'] + " added to games cache")

                self.owned_games_cache.append(
                    Game(
                        program['id'],
                        program['ProductName'],
                        None,
                        LicenseInfo(LicenseType.SinglePurchase, None)
                    )
                )

        return self.owned_games_cache

    def delete_existent_game_entry(self, installer_uuid):
        # Searches for owned games which are already installed and marks them as installed with proper game path
        for owned_game in self.games:
            if owned_game[0] == installer_uuid:
                self.games.remove(owned_game)

    async def get_local_games(self):
        return self.local_games_list()

    async def launch_game(self, game_id: str) -> None:
        for game in self.games:
            if game[0] == game_id:
                # launch game from exe
                subprocess.Popen(game[1] + r"\\" + game[2])
                # Set game as running
                logger.info("Game " + game[0] + " is running")
                Plugin.update_local_game_status(self,
                                                LocalGame(game[0], LocalGameState.Installed | LocalGameState.Running))
                for local_game in self.local_games_status:  # Also update cache
                    if local_game.game_id == game[0]:
                        local_game.local_game_state = LocalGameState.Installed | LocalGameState.Running

    async def install_game(self, game_id: str) -> None:
        await self.launch_platform_client()

    async def uninstall_game(self, game_id: str) -> None:
        for game in self.games:
            if game[0] == game_id:
                subprocess.Popen(
                    game[1] + "\\Uninstall.exe")  # uninstall game from exe, common to all games

        # self.update_local_game_status(LocalGame(game_id, LocalGameState.None_))
        # self._local_games_cache.pop(game_id)

    def local_games_list(self):
        self.local_games_status.clear()

        # only adding installed games
        for game in self.games:
            logger.info(game)

            if game[1] is None:
                # Game not installed
                self.local_games_status.append(
                    LocalGame(
                        str(game[0]),
                        LocalGameState.None_
                    )
                )
            else:
                # Game installed
                self.local_games_status.append(
                    LocalGame(
                        str(game[0]),
                        LocalGameState.Installed
                    )
                )
        return self.local_games_status

    def is_running(self, game_id: str):
        game_path = Path

        for game in self.games:
            if game[0] == game_id:
                game_path = Path(game[1] + r"\\" + game[2])

        for proc in process_iter():
            if proc.binary_path and Path(proc.binary_path).resolve() == game_path:
                return True

        return False

    # to-do
    def update_owned_games(self):
        if (time() - self._owned_games_last_updated) < OWNED_GAMES_TIMEOUT:
            return
        logger.info("Passed timeout, checking for newer games")
        self.get_owned_games()

        # for game in self.owned_games_cache:

        self._owned_games_last_updated = time()

    def tick(self):
        self.change_game_running_status()
        self.update_owned_games()

    def change_game_running_status(self):
        for game in self.local_games_status:
            # logger.info(game.local_game_state)
            if game.local_game_state == LocalGameState.Installed | LocalGameState.Running:
                if not self.is_running(game.game_id):  # Game isn't running anymore
                    logger.info("Game " + game.game_id + " is not running anymore")
                    game.local_game_state = LocalGameState.Installed
                    Plugin.update_local_game_status(self, LocalGame(game.game_id, LocalGameState.Installed))


def main():
    create_and_run_plugin(LegacyGamesPlugin, sys.argv)


# run plugin event loop
if __name__ == "__main__":
    main()
