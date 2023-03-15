# **Legacy Games integration for GOG Galaxy 2.0**


## Currently supported features
- Import installed games
- Import games redeemed from Amazon Prime
- Launch games
- install games (*)
- Uninstall games
- Playing status

## Issues
- (*) clicking the "install" button on a game will open the launcher as intended, but until it isn't closed, the plugin will be marked as offline; in that case you'll have to press the "retry" button to make it working again
- (*)the "install" button may appear and disappear randomly
- uninstalling a game may not update the installed status on Galaxy until doing a reboot, I'm working on a fix (low priority)

## Credits
The plugin is based on work done by others, especially from:
- https://github.com/Rall3n/galaxy-integration-amazon used as a base for this plugin
- https://github.com/Jeshibu/PlayniteExtensions/tree/main/source/LegacyGamesLibrary used for learning how the Legacy Games Launcher backend works