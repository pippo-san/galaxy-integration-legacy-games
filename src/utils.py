import winreg as registry

from galaxy.api.plugin import logger


def _get_reg_value(regKey, valueKey):
    try:
        return registry.QueryValueEx(regKey, valueKey)[0]
    except OSError:
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
