import json
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
from utils import get_uninstall_programs_list
from game_fixes import check_available_fixes

__version__ = 0.1

# load launcher configuration
logger.info("opening json")
path = os.getenv('APPDATA')

launcherJSON = path + "\\legacy-games-launcher\\app-state.json"

file = open(launcherJSON, encoding="utf8")
f = json.load(file)

username = f["user"]["profile"]["username"]
# userId = f["user"]["profile"]["id"]
install_path = f["settings"]["gameLibraryPath"][0]

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

    async def authenticate(self, stored_credentials=None):
        logger.info("started authentication")
        user_data = {'username': username}
        self.store_credentials(user_data)
        return Authentication("LegacyGames", username)

    async def pass_login_credentials(self, step: str, credentials: Dict[str, str], cookies: List[Dict[str, str]]) -> \
            Union[NextStep, Authentication]:
        logger.info("passing cached login credentials")
        logger.info("started authentication")
        user_data = {'username': username}
        self.store_credentials(user_data)
        return Authentication("LegacyGames", username)

    async def launch_platform_client(self):
        LegacyGamesClient.start_client()

    async def shutdown_platform_client(self):
        self.client_path.stop_client()

    async def get_os_compatibility(self, game_id, context):
        return OSCompatibility.Windows

    async def get_owned_games(self) -> List[Game]:
        # Clear games list from previously imported games
        self.games.clear()
        self.owned_games_cache.clear()

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

                # lista dei giochi con percorso d'installazione ed eseguibile
                self.games.append(
                    [program['id'], program['InstDir'], program['GameExe']]
                )

                # lista Galaxy dei giochi
                logger.info("Game " + program['id'] + " added to games cache")

                fixed_game = check_available_fixes(program['id'])

                if fixed_game is not None:
                    logger.info("A fix is available for the game")
                    self.owned_games_cache.append(fixed_game)
                else:
                    self.owned_games_cache.append(
                        Game(
                            program['id'],
                            program['ProductName'],
                            None,
                            LicenseInfo(LicenseType.SinglePurchase, None)
                        )
                    )

        return self.owned_games_cache

    async def get_local_games(self):
        return self.local_games_list()

    async def launch_game(self, game_id: str) -> None:
        for game in self.games:
            if game[0] == game_id:
                subprocess.Popen(game[1] + r"\\" + game[2])  # lancio il gioco dall'eseguibile
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
                    game[1] + "\\Uninstall.exe")  # disinstallo il gioco dall'eseguibile, uguale per tutti

        # self.update_local_game_status(LocalGame(game_id, LocalGameState.None_))
        # self._local_games_cache.pop(game_id)

    # aggiungo solo giochi installati
    def local_games_list(self):
        self.local_games_status.clear()

        for game in self.games:
            logger.info(game)
            # logger.info("Inserisco | " + game[0] + " | fra i giochi locali")
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
