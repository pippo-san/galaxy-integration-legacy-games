import asyncio
import json
import os
import subprocess
import winreg as registry
from pathlib import Path

from galaxy.api.plugin import logger
from galaxy.proc_tools import process_iter

from utils import _get_reg_value

class LegacyGamesClient:
    _CLIENT_NAME_ = 'Legacy Games'

    def __init__(self):
        self.install_location = get_launcher_path()

    @staticmethod
    def _exec(args, cwd=None):
        subprocess.Popen(
            args,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
            cwd=cwd,
            shell=False
        )

    async def _aexec(self, args, cwd=None):
        proc = await asyncio.create_subprocess_exec(*args)
        return await proc.wait()

    @property
    def is_running(self):
        for proc in process_iter():
            if proc.binary_path and Path(proc.binary_path).resolve() == self.exec_path:
                return True

        return False

    @property
    def exec_path(self):
        if not self.install_location:
            return ''

        return self.install_location.joinpath("Legacy Games Launcher.exe")

    def start_client(self):
        if self.install_location is not None:
            logger.info(os.system('"' + self.install_location + '\Legacy Games Launcher.exe' + '"'))

    def stop_client(self):
        if self.is_running:
            LegacyGamesClient._exec(f'taskkill /t /f /im "Legacy Games Launcher.exe"')


def open_launcher_config_file():
    logger.info("opening json")
    path = os.getenv('APPDATA')

    launcherJSON = path + "\\legacy-games-launcher\\app-state.json"

    file = open(launcherJSON, encoding="utf8")
    f = json.load(file)

    return f


def get_launcher_path():
    key = registry.HKEY_LOCAL_MACHINE
    subKey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
    regKey = registry.OpenKey(key, subKey, 0, registry.KEY_READ | registry.KEY_WOW64_64KEY)
    keys, _, _ = registry.QueryInfoKey(regKey)
    logger.info("Searching for launcher path")
    for i in range(keys):
        with registry.OpenKey(regKey, registry.EnumKey(regKey, i), 0, registry.KEY_READ | registry.KEY_WOW64_64KEY) as itemKey:
            reg_value = _get_reg_value(itemKey, 'DisplayIcon')
            if reg_value is not None:
                if "Legacy Games Launcher" in reg_value:
                    launcherPath = reg_value.replace(r"\uninstallerIcon.ico", "")
                    logger.info("Launcher path set as "+launcherPath)
                    return launcherPath
    logger.info("Launcher path not found")
    return None
