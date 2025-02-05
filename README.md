# LauncherBlast2-reBoot

### This fork has the following features:

- A master server browser. You can view online SRB2 servers and select one to join.
- A mod browser and installer. See a list of mods from the SRB2 message board, and click a button to download them.
- Support for multiple settings profiles.
- Settings and profiles are saved as easily editable TOML files (similar to INI files).
- Multithreading, to avoid GUI freezing.

### Generating Qt .py file from .ui file
```pyside6-uic lb2.ui -o lb2_ui.py ```

### Notes
If you add new GUI widgets, don't forget to make them save to the settings TOML file!

![](ms_list_screenshot.png)

![](mod_downloader_screenshot.png)