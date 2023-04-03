
class Game():
    """
    Game is an object that has a game_title, game_date, and game_stats
    This is how each month of game data is stored, directly from each row in the datafile
    """

    def __init__(self, game_title, game_date, game_stats):
        self.game_title = game_title
        self.game_date = game_date
        self.game_stats = game_stats
    
    def get_title(self):
        return self.game_title

    def get_date(self):
        return self.game_date

    def get_stats(self):
        return self.game_stats
