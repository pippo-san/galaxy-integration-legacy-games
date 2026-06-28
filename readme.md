# **Legacy Games integration for GOG Galaxy 2.0+**
GOG Galaxy Integration to import Legacy Games game titles.

This plugin is only supported on Windows and requires the Legacy Games Launcher to be installed on the system.

## Currently supported features
- Import installed games
- Import games redeemed from Amazon Prime
- Install games (*)
- Launch games
- Playing status
- Uninstall games
- Game time (when launched trough Galaxy)

## Installation
1) Download the [latest version avaliable](https://github.com/pippo-san/galaxy-integration-legacy-games/releases/latest) of the integration, making sure to select the correct one in regards to the installed GOG Galaxy version (2.1 for 2.1 version and above, otherwise use 2.0)
2) unzip the folder into `%LOCALAPPDATA%\GOG.com\Galaxy\plugins\installed`. The directory tree should look like this:

```
├── Integration_1
├── Integration_2
├── ...
└── LegacyGames
    ├── dependency_1
    ├── dependency_2
    ├── ...
    ├── plugin.py
    ├── manifest.json
    ├── ...

```


## Issues
- (*) the "install" button may appear and disappear randomly (if you right-click into the game tile, when on the library view, the install button will always be there. May be a galaxy bug)
- uninstalling a game may not update the installed status on Galaxy until doing a reboot, I'm working on a fix (low priority)
- some titles may not be recognised correctly, please see issue https://github.com/pippo-san/galaxy-integration-legacy-games/issues/9

## Credits
The plugin is based on work done by others, especially from:
- https://github.com/Rall3n/galaxy-integration-amazon used as a base for this plugin
- https://github.com/Jeshibu/PlayniteExtensions/tree/main/source/LegacyGamesLibrary used for learning how the Legacy Games Launcher backend works

I would also like to thank you, @tylerbrawl, for creating the awesome [Galaxy-Utils](https://github.com/tylerbrawl/Galaxy-Utils), because, without them, time tracking wouldn't have been so easy to implement
