import time
import sys

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Signal

from networking import mb_query
from networking.ms_query import get_server_list, ms_url, ms_kart_url
from select_item_dialog import SelectItemDialog

class QueryMessageBoard(QtCore.QThread):
    # Emits a string describing the mod
    mod_description_sig1 = Signal(object)
    # Emits a list of mods
    mod_list_sig1 = Signal(dict)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.mod = None
        self.get_mod_description = False
        self.get_mods = False
        self.mods_type = None

    def on_request_mod_list(self, mods_type):
        self.get_mods = True
        self.mods_type = mods_type

    def on_request_mod_desc(self, mod):
        print("on_request_mod_desc")
        self.mod = mod

    # TODO create exceptions for MB not loading
    def run(self):
        self.running = True
        while self.running:
            if self.get_mods:
                self.mods_list = {}
                subforum_url = None
                if self.mods_type == "Maps":
                    subforum_url = mb_query.maps_sublink
                if self.mods_type == "Characters":
                    subforum_url = mb_query.characters_sublink
                if self.mods_type == "Lua":
                    subforum_url = mb_query.lua_sublink
                if self.mods_type == "Assets":
                    subforum_url = mb_query.assets_sublink
                if self.mods_type == "Misc":
                    subforum_url = mb_query.misc_sublink
                mods = mb_query.get_mods(subforum_url)
                for mod in mods:
                    entry_text = mod.name
                    self.mods_list[entry_text] = mod

                self.mod_list_sig1.emit(self.mods_list)

                # Reset variables
                self.mods_list = {}
                self.get_mods = False
                self.mods_type = None

            if self.mod:
                self.mod.get_description()
                self.mod_description_sig1.emit(self.mod)

                # Reset variables
                self.mod = None

            time.sleep(1)


class QueryMasterServer(QtCore.QThread):
    server_list_sig1 = Signal(list)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.query_ms = False
        self.running = True
    
    def on_refresh(self):
        """Refresh button clicked
        """
        self.query_ms = True
        
    def on_quit(self):
        self.running = False
        
    def run(self):
        while self.running:
            if self.query_ms:
                server_list = get_server_list(ms_url)
                self.server_list_sig1.emit(server_list)
                self.query_ms = False                    
            time.sleep(1)


class ModDownloader(QtCore.QThread):
    mod_filepath_sig1 = Signal(list)
    
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.download_urls = None
        self.filepath = None
        self.running = True
        
    def on_download_button(self, mod):
        self.download_urls = mod.get_download_urls()
        
    def on_filepath_emit(self, filepath):
        self.filepath = filepath
        
    def run(self):
        while self.running:
            if self.download_urls and self.filepath:

                filepaths = []
                mod_selection = None
                if len(self.download_urls) > 1:
                    dialog = SelectItemDialog(self.download_urls)
                    r = dialog.exec()
                    mod_selection = dialog.get_selected_items()
                else:
                    mod_selection = self.download_urls

                for name, url in mod_selection:
                    # TODO download selector popup box
                    print("Remove this later and uncomment the next line")
                    filepaths.append(mb_query.download_mod(self.filepath, url))
                    # Extract files, get wads/pk3/etc to add.

                self.mod_filepath_sig1.emit([filepaths])
                #print(filepaths)
                self.download_button_url = None
                self.filepath = None
            time.sleep(1)
