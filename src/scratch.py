# import os
# import winreg as registry
#
# uninstall_key = r"SOFTWARE\Legacy Games"
#
# key = registry.HKEY_CURRENT_USER
# subKey = uninstall_key
#
# entries = []
# regKey = registry.OpenKey(key, subKey)
# keys, _, _ = registry.QueryInfoKey(regKey)
#
#
# def _get_reg_value(regKey, valueKey):
#    try:
#        return registry.QueryValueEx(regKey, valueKey)[0]
#    except OSError:
#        return None
#
#
# for i in range(keys):
#    with registry.OpenKey(regKey, registry.EnumKey(regKey, i)) as itemKey:
#        game = {'id': _get_reg_value(itemKey, 'InstallerUUID'),
#                'ProductName': _get_reg_value(itemKey, 'ProductName'),
#                'InstDir': _get_reg_value(itemKey, 'InstDir'),
#                'GameExe': _get_reg_value(itemKey, 'GameExe')}
#        print(game['id'])
#        entries.append(game)
#
# print(entries)
# for game in entries:
#    print("Imported game --> id " + game['id'] + " | path " + game['InstDir'])
import os
import subprocess

#path = "C:\\Program Files\\Legacy Games\\Legacy Games Launcher\\Legacy Games Launcher.exe'"
#os.system('start C:\\Program Files\\Legacy Games\\Legacy Games Launcher\\Legacy Games Launcher.exe')

subprocess.call(['runas', '/user:Administrator', 'C:\\Program Files\\Legacy Games\\Legacy Games Launcher\\Legacy Games Launcher.exe'])