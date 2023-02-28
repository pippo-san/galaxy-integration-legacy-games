import json
import os
import winreg as registry
from pathlib import Path

from galaxy.api.plugin import logger
from galaxy.proc_tools import process_iter


def open_launcher_config_file():
    logger.info("opening json")
    path = os.getenv('APPDATA')

    launcherJSON = path + "\\legacy-games-launcher\\app-state.json"

    file = open(launcherJSON, encoding="utf8")
    f = json.load(file)

    return f


def _get_reg_value(regKey, valueKey):
    try:
        return registry.QueryValueEx(regKey, valueKey)[0]
    except OSError:
        return None

def is_running(program_path: Path):
    for proc in process_iter():
        if proc.binary_path and Path(proc.binary_path).resolve() == program_path:
            return True
    return False

def get_launcher_path():
    key = registry.HKEY_LOCAL_MACHINE
    subKey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
    regKey = registry.OpenKey(key, subKey)
    keys, _, _ = registry.QueryInfoKey(regKey)
    logger.info("Searching for launcher path")
    for i in range(keys):
        with registry.OpenKey(regKey, registry.EnumKey(regKey, i)) as itemKey:
            reg_value = _get_reg_value(itemKey, 'DisplayName')
            if _get_reg_value(itemKey, 'DisplayName') is not None:
                if "Legacy Games Launcher" in reg_value:
                    print(reg_value)
                    iconPath = _get_reg_value(itemKey, 'DisplayIcon')
                    launcherPath = iconPath.replace(r"\uninstallerIcon.ico", "")
                    logger.info("Launcher path set as "+launcherPath)
                    return launcherPath
    logger.info("Launcher path not found")
    return None

def get_uninstall_programs_list():
    key = registry.HKEY_CURRENT_USER
    subKey = r"SOFTWARE\Legacy Games"

    entries = []
    regKey = registry.OpenKey(key, subKey)
    keys, _, _ = registry.QueryInfoKey(regKey)

    logger.info("Reading games from registry")
    for i in range(keys):
        with registry.OpenKey(regKey, registry.EnumKey(regKey, i)) as itemKey:
            game = {'id': _get_reg_value(itemKey, 'InstallerUUID'),
                    'ProductName': _get_reg_value(itemKey, 'ProductName'),
                    'InstDir': _get_reg_value(itemKey, 'InstDir'),
                    'GameExe': _get_reg_value(itemKey, 'GameExe')
                    }
            logger.info("Detected game --> id " + game['id'] + " | path " + game['InstDir'])
            entries.append(game)
    return entries
