import ctypes
import os
import pickle
import subprocess
import sys
from pathlib import Path
from time import time
from typing import List, Dict, Union, Any

from galaxy.api.consts import Platform, OSCompatibility, LocalGameState, LicenseType, Feature
from galaxy.api.plugin import Plugin, create_and_run_plugin, logger
from galaxy.api.types import Authentication, Game, LocalGame, LicenseInfo, NextStep, GameTime
from galaxy.proc_tools import process_iter
from galaxyutils.time_tracker import TimeTracker, GameNotTrackedException, GamesStillBeingTrackedException

from client import LegacyGamesClient, open_launcher_config_file
from utils import get_uninstall_programs_list
from game_fixes import check_available_fixes

__version__ = "0.2.1"

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

        self.client = LegacyGamesClient()
        self.games = []  # [id, InstDir, GameExe]
        self.owned_games_cache = []  # Game obj
        self.local_games_status = []  # LocalGame obj

        self.config_file = open_launcher_config_file()

        try:
            self.username = self.config_file["user"]["profile"]["username"]
            # userId = f["user"]["profile"]["id"]
        except KeyError:
            self.username = "Legacy Games User"

        self.install_path = self.config_file["settings"]["gameLibraryPath"][0]

        if sys.platform == 'win32':
            self.buffer = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, self.buffer)
            self.documents_location = self.buffer.value

        self.game_time_cache = None
        self.game_time_tracker = None

        self.init_game_time_cache()

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

    def launch_platform_client(self):
        self.client.start_client()

    async def shutdown_platform_client(self):
        # the code is there, but killing a 64 bit process in a 32bit environment isn't easy
        pass

    async def get_os_compatibility(self, game_id, context):
        return OSCompatibility.Windows

    def get_giveaway_games(self):
        for game in self.config_file["user"]["giveawayDownloads"]:
            game_id = game["installer_uuid"]
            self.games.append(
                [game_id, None, None]
            )
            game_name = self.find_game_title(game['installer_uuid'])

            # Check for library fixes
            fixed_game = check_available_fixes(game['installer_uuid'])

            logger.info("Game " + game['installer_uuid'] + " added to owned games, with name " + game_name)
            if fixed_game is not None:
                logger.info("A fix is available for the game " + game['installer_uuid'])
                self.owned_games_cache.append(fixed_game)
            else:
                self.owned_games_cache.append(
                    Game(
                        game['installer_uuid'],
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
                    continue

                # So we don't have multiple entries of the same game
                self.delete_existent_game_entry(program['id'])

                # games list with install directory and exe
                self.games.append(
                    [program['id'], program['InstDir'], program['GameExe']]
                )

                # Galaxy games list
                logger.info("Game " + program['id'] + " added to games cache")

                # Check for library fixes
                fixed_game = check_available_fixes(program['id'])

                if fixed_game is not None:
                    logger.info("A fix is available for the game "+program['id'])
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

                # Start tracking game time
                self.game_time_tracker.start_tracking_game(game_id)

    async def install_game(self, game_id: str) -> None:
        self.launch_platform_client()

    async def uninstall_game(self, game_id: str) -> None:
        for game in self.games:
            if game[0] == game_id:
                subprocess.Popen(
                    game[1] + "\\Uninstall.exe")  # uninstall game from exe, common to all games

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

    def init_game_time_cache(self):
        # Check the persistent cache first.
        if "game_time_cache" in self.persistent_cache:
            logger.info("Loading game time cache from persistent cache")
            self.game_time_cache = pickle.loads(bytes.fromhex(self.persistent_cache["game_time_cache"]))
        # If the game time cache cannot be found in the persistent cache, then check a local file for it.
        else:
            try:
                file_location = os.path.join(self.documents_location, "LegacyGamesPlayTimeCache.txt")
                file = open(file_location, "r")
                logger.info("Loading game time cache from file")
                for line in file.readlines():
                    if line[:1] != "#":
                        self.game_time_cache = pickle.loads(bytes.fromhex(line))
                        break
            except FileNotFoundError:
                # If the file does not exist, then use an empty game time cache.
                self.game_time_tracker = TimeTracker()
                return
        self.game_time_tracker = TimeTracker(game_time_cache=self.game_time_cache)

    async def get_game_time(self, game_id: str, context: Any) -> GameTime:
        try:
            game_time = self.game_time_tracker.get_tracked_time(game_id)
        except GameNotTrackedException:
            # Game never tracked
            game_time = None
        return game_time

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

                    # Stop tracking game time
                    self.game_time_tracker.stop_tracking_game(game.game_id)
                    self.update_game_time(self.game_time_tracker.get_tracked_time(game.game_id))

    async def shutdown(self) -> None:
        logger.debug("Pushing the cache of played game times to the persistent cache...")

        try:
            self.game_time_cache = self.game_time_tracker.get_time_cache()
        except GamesStillBeingTrackedException:
            for game in self.local_games_status:
                if game.local_game_state == LocalGameState.Installed | LocalGameState.Running:
                    self.game_time_tracker.stop_tracking_game(game.game_id)

            self.game_time_cache = self.game_time_tracker.get_time_cache()

        self.persistent_cache['game_time_cache'] = pickle.dumps(self.game_time_cache).hex()
        self.push_cache()

        file_location = os.path.join(self.documents_location, "LegacyGamesPlayTimeCache.txt")
        file = open(file_location, "w+")
        # Consider informing the user to not modify the game time cache file.
        file.write("# This file contains a cached copy of the user's play time for the Legacy Games Integration for GOG"
                   " Galaxy 2.0.\n")
        file.write("# DO NOT EDIT THIS FILE IN ANY WAY!\n"
                   )
        file.write(self.game_time_tracker.get_time_cache_hex())
        file.close()


def main():
    create_and_run_plugin(LegacyGamesPlugin, sys.argv)


# run plugin event loop
if __name__ == "__main__":
    main()
