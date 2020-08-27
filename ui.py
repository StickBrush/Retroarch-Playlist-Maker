from database import Database
import logging
from sys import stderr

class InteractiveSearch:

    def __init__(self, db: Database):
        self.db = db
        self._latest = []
        self._logger = logging.getLogger("InteractiveSearch")
        self._logger.debug("Ready")
    
    def do_interactive_search(self):
        sys_name = None
        refine = input("Refine the search specifying the console? y/N\n")
        if refine.lower() == 'y':
            for ndx, system in enumerate(self.db.get_available_systems()):
                print("{}) {}".format(ndx+1, system))
            sys_num = -1
            while sys_num < 1 or sys_num > len(self.db.get_available_systems()):
                sys_num = input("Console number: ")
                try:
                    sys_num = int(sys_num)
                    sys_num -= 1
                    if sys_num < 0 or sys_num >= len(self.db.get_available_systems()):
                        print("Console not found", file=stderr)
                except ValueError:
                    print("ERROR: Not a number", file=stderr)
            sys_name = self.db.get_available_systems()[sys_num]
        user_input = input("Search in the database:\n")
        if sys_name is not None:
            self._latest = self.db.query_system(sys_name, user_input)
        else:
            self._latest = self.db.query_all_systems(user_input)
    
    def choose_from_latest(self, limit: int = 30) -> tuple:
        if len(self._latest) == 0:
            print("ERROR: No results!", file=stderr)
        else:
            show = self._latest[:limit]
            for ndx, data in enumerate(show):
                (game, system) = data
                print("{}) {} ({})".format(ndx+1, game, system))
            game_num = -1
            while game_num < 1 or game_num > len(show):
                game_num = input("Game number: ")
                try:
                    game_num = int(game_num)
                    game_num -= 1
                    if game_num < 0 or game_num >= len(self.db.get_available_systems()):
                        print("Game not found", file=stderr)
                except ValueError:
                    print("ERROR: Not a number", file=stderr)
            return show[game_num]