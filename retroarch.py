import json
import os
import logging
from uuid import uuid4 as getUUID

class Game:

    PATH_LABEL = "path"
    LABEL_LABEL = "label"
    CORE_PATH_LABEL = "core_path"
    CORE_NAME_LABEL = "core_name"
    CRC32_LABEL = "crc32"
    DB_NAME_LABEL = "db_name"

    def __init__(self, base_dict: dict = {}):
        self.path = base_dict.get(self.PATH_LABEL, "")
        self.label = base_dict.get(self.LABEL_LABEL, "")
        self.core_path = base_dict.get(self.CORE_PATH_LABEL, "DETECT")
        self.core_name = base_dict.get(self.CORE_NAME_LABEL, "DETECT")
        self.crc32 = base_dict.get(self.CRC32_LABEL, "DETECT")
        self.db_name = base_dict.get(self.DB_NAME_LABEL, "")
        self._id = str(getUUID())
        self._logger = logging.getLogger("Game-{}".format(self._id))
        if base_dict != {}:
            self._logger.debug("Loaded game - {}".format(self.label))
        self._logger.debug("Ready")
    
    def to_dict(self) -> dict:
        dkt = {
            self.PATH_LABEL: self.path,
            self.LABEL_LABEL: self.label,
            self.CORE_PATH_LABEL: self.core_path,
            self.CORE_NAME_LABEL: self.core_name,
            self.CRC32_LABEL: self.crc32,
            self.DB_NAME_LABEL: self.db_name
        }
        self._logger.debug("Serialized: {}".format(dkt))
        return dkt

class Playlist:

    DEFAULTS = {
        "version": "1.4",
        "default_core_path": "",
        "default_core_name": "",
        "label_display_mode": 0,
        "right_thumbnail_mode": 0,
        "left_thumbnail_mode": 0,
        "sort_mode": 0,
    }
    
    ITEMS_KEY = "items"

    def __init__(self, override_defaults: dict = {}):
        self._id = str(getUUID())
        self._logger = logging.getLogger("Playlist-{}".format(self._id))
        self._inner_pl = self.DEFAULTS
        for key in override_defaults:
            self._inner_pl[key] = override_defaults[key]
        self._inner_pl[self.ITEMS_KEY] = []
        self._games = []
        self._lut = []
        self._logger.debug("Ready")
    
    def load(self, playlist_fname: str):
        if not os.path.exists(playlist_fname):
            self._logger.error("Could not load playlist on {}".format(playlist_fname))
        else:
            self._games = []
            self._lut = []
            with open(playlist_fname, 'r') as in_json:
                self._inner_pl = json.load(in_json)
            for item in self._inner_pl.get(self.ITEMS_KEY, []):
                self._games.append(Game(item))
            self._logger.info("Loaded playlist - {} elements".format(len(self._games)))
    
    def save(self, playlist_fname: str):
        if os.path.exists(playlist_fname):
            self._logger.warning("Overwriting file {}".format(playlist_fname))
        os.makedirs(os.path.dirname(playlist_fname), exist_ok=True)
        db_name = os.path.split(playlist_fname)[-1]
        if not self.ITEMS_KEY in self._inner_pl:
            self._inner_pl[self.ITEMS_KEY] = []
        for game in self._games:
            game.db_name = db_name
            self._inner_pl[self.ITEMS_KEY].append(game.to_dict())
        with open(playlist_fname, 'w') as out_json:
            json.dump(self._inner_pl, out_json)
        self._logger.info("Saved playlist - {} elements".format(len(self._games)))
        self._logger.info("Find it on {}".format(playlist_fname))

    def add_game(self, game: Game):
        if not game.path in self._lut:
            self._games.append(game)
            self._lut.append(game.path)
            self._logger.debug("Added game - {}".format(game.label))
        else:
            self._logger.debug("Game {} already in").__format__(game.label)
