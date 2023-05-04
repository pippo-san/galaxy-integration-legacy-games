# **Legacy Games integration for GOG Galaxy 2.0**


## Currently supported features
- Import installed games
- Import games redeemed from Amazon Prime
- Install games (*)
- Launch games
- Playing status
- Uninstall games
- Game time (when launched trough Galaxy)

## Issues
- (*) the "install" button may appear and disappear randomly (if you right-click into the game tile, when on the library view, the install button will always be there. May be a galaxy bug)
- uninstalling a game may not update the installed status on Galaxy until doing a reboot, I'm working on a fix (low priority)

## Credits
The plugin is based on work done by others, especially from:
- https://github.com/Rall3n/galaxy-integration-amazon used as a base for this plugin
- https://github.com/Jeshibu/PlayniteExtensions/tree/main/source/LegacyGamesLibrary used for learning how the Legacy Games Launcher backend works

I would also like to thank you, @tylerbrawl, for creating the awesome [Galaxy-Utils](https://github.com/tylerbrawl/Galaxy-Utils), because, without them, time tracking wouldn't have been so easy to implement
