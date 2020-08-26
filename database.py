import xml.etree.ElementTree as ET
import os
import re
import logging
import pickle

from fuzzywuzzy import process

class Database:

    @staticmethod
    def std_name(name: str) -> str:
        std_name = re.sub('[(][^)]*[)]', '', name)
        std_name = std_name.strip()
        return std_name

    def __init__(self, databases: list, accelerate_file: str = None):
        self._databases = {}
        self._logger = logging.getLogger('Database')
        loaded = False
        if accelerate_file is not None:
            try:
                with open(accelerate_file, 'rb') as in_xlr8:
                    self._databases = pickle.load(in_xlr8)
                    loaded = True
                    self._logger.info("Loaded accelerate file")
            except Exception:
                self._logger.error("Could not load accelerate file")
        if not loaded:
            for datfile in databases:
                try:
                    xml = ET.parse(datfile)
                    root = xml.getroot()
                    name = root.find('header').find('name').text
                    name = self.std_name(name)
                    database = {}
                    games = root.findall('game')
                    for game in games:
                        gname = None
                        try:
                            gname = game.attrib['name']
                            crc = game.find('rom').attrib['crc']
                            database[gname] = crc
                        except Exception:
                            if gname is None:
                                self._logger.warning('No ROM for {}'.format(game))
                            else:
                                self._logger.warning('No ROM for {}'.format(gname))
                    self._databases[name] = database
                    self._logger.info('Loaded system {} - {} games'.format(name, len(database)))
                except Exception:
                    self._logger.error("Could not load file {}".format(datfile))
        self._logger.info('Loaded database - {} systems available'.format(len(self._databases)))
    
    def get_available_systems(self) -> list:
        return list(self._databases.keys())
    
    def save_accelerate_file(self, accelerate_file: str):
        if os.path.exists(accelerate_file):
            self._logger.warning("Overwriting previous file")
        os.makedirs(os.path.dirname(accelerate_file), exist_ok=True)
        try:
            with open(accelerate_file, 'wb') as out_xlr8:
                pickle.dump(self._databases, out_xlr8)
                self._logger.info("Saved accelerate file")
        except Exception:
            self._logger.error("Could not save accelerate file")

    def query_system(self, system: str, query: str) -> list:
        if system not in self._databases:
            return []
        else:
            curr_db = self._databases[system]
            g_names = [str(k) for k in curr_db]
            ratios = process.extract(query, g_names, limit=100)
            sorted_ratios = sorted(ratios, key=lambda x: x[1], reverse=True)
            return [item[0] for item in sorted_ratios]
    
    def query_all_systems(self, query: str) -> list:
        all_ratios = []
        for system in self._databases:
            curr_db = self._databases[system]
            g_names = [str(k) for k in curr_db]
            ratios = process.extract(query, g_names, limit=20)
            ratios = list(map(lambda x: (x[0]+' - '+system, x[1]), ratios))
            all_ratios.extend(ratios)
        sorted_ratios = sorted(all_ratios, key=lambda x: x[1], reverse=True)
        return [item[0] for item in sorted_ratios]
        
        
    