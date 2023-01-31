# **Legacy Games integration for GOG Galaxy 2.0**


## Currently supported features
- Import installed games
- Launch games
- Uninstall games
- Playing status

## Issues
- launcher may require admin privileges, in that case, won't be possible to launch it. If doing so, next time you'll open the launcher, it will show up as in offline mode.
- uninstalling a game may not update the installed status on Galaxy until doing a reboot, I'm working on a fix

## Credits
The plugin is based on work done by others, especially from:
- https://github.com/Rall3n/galaxy-integration-amazon used as a base for this plugin
- https://github.com/Jeshibu/PlayniteExtensions/tree/main/source/LegacyGamesLibrary used for learning how the Legacy Games Launcher backend works