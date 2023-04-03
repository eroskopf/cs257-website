import psycopg2
import psqlConfig
import game
import matplotlib.pyplot as plt
from datetime import *
from dateutil.relativedelta import relativedelta


def _fill_out_data(uncertain_list, start, end):
    """
    A helper function to fill out the missing data so that there is a game object for every 
    month from the start month to the end month. If the list doesn't have value for a month, 
    like if it dropped out of the top 100 games that this dataset tracks, adds that date 
    with a placeholder value of 0 into the list.
    
    Parameters:
        uncertain_list - a list full of Game objects that may not be complete
        start - a datetime object that should be the date of the first object in the list
        end - a datetime object that should be the date of the last object in the list
    
    Return:
        a list with values for every month between the start month and the end month
    """
    final_list = []
    uncertain_list.reverse()
    current_list = uncertain_list
    current_date = start
    one_month_past_end = _increment_month(end)
    while len(current_list) > 0:
        if current_date == _remove_time(current_list[0].get_date()):
            final_list.append(current_list.pop(0))
        else:
            final_list.append(game.Game(uncertain_list[0].get_title(), current_date, 0))
        current_date = _increment_month(current_date)
    #appending empty games to fill out the whole timeframe of interest
    while current_date != one_month_past_end:
        final_list.append(game.Game(uncertain_list[0].get_title(), current_date, 0))
        current_date = _increment_month(current_date)
    return final_list

def _remove_time(old_date):
    """
    A helper method that removes the time information off of a date
   
    Parameters:
        old_date - a datetime object with the time information
   
    Return:
        a datetime object with only the month, year, and day
    """
    new_date = date(old_date.year, old_date.month, old_date.day)
    return new_date

def _increment_month(old_date):
    """
    A helper method that adds one month to the current date, keeping the day as the first of the month and
    flipping years when necessary. Uses dateutil.relativedelta
    
    Parameters:
        old_date - a datetime object that needs to be incremented
    
    Return:
        a datetime object that has been incremented one month later
    """
    incremented_date = old_date + relativedelta(months=1)
    return _remove_time(incremented_date)

def _to_datetime(year, month):
    """
    A helper method that takes in a string year and month, and turns it into a datetime with the proper
    year, month, and the first day of the month. Days are never used in this file or anywhere else, but
    the datetime object has several methods that we need to use which is they we're not just storing
    months and years. 
   
   Parameters:
        year - a string of the year
        month - a string of the month
    
    Return:
        a datetime object of the year and month
    """
    return _remove_time(datetime(int(year), int(month), 1))

def _list_of_game_objects(tuple_list):
    """
    A helper method to take the list of tuples that psycopg2 returns and makes each item in the list
    a Game object
    
    Parameters:
        tuple_list - a list that psycopg2 returns from the database
    
    Return:
        a list of game objects, each with the game_title, game_stats, and game_date
    """
    return_list = []
    for tup in tuple_list:
        g = game.Game(tup[2], tup[1], tup[0])
        return_list.append(g)
    return return_list


def _prep_list(game_list):
    """
    a helper method that takes in a list of game objects and outputs a list of dates
    and statistics of each game, preserving the original order
    Parameters:
        game_list: a list of game objects

    Returns:
        a list containing two lists, one with the dates, and one with the stats

    """
    dates = []
    stats = []
    for g in game_list:
        dates.append(g.get_date())
        stats.append(g.get_stats())
    return_list = [dates, stats]
    return return_list

def _save_graph(game1_list, game2_list):
    """
    a helper method that takes in two lists of game objects and graphs the dates and stats. This graph
    is then saved into the static directory under the name result_image.png.
    Parameters:
        game1_list: a list of game objects for the first game of interest
        game2_list: a list of game objects for the second game of interest

    Returns:
        nothing. it just saves the image 
    """
    game1 = _prep_list(game1_list)
    game2 = _prep_list(game2_list)
    plt.plot(game1[0], game1[1], color='purple')
    plt.plot(game2[0], game2[1], color='blue', ls='--')
    plt.xlabel('Time', fontsize= 12)
    plt.xticks(fontsize=8, rotation=45, ha='right')
    plt.ylabel('Number of Players on Steam', fontsize=12)
    plt.yticks(fontsize=16, rotation=90, va='center')
    plt.title('Results Graph: ' + str(game1_list[0].get_title()) + " and " + str(game2_list[0].get_title()))
    plt.subplots_adjust(left=0.15, bottom=0.2, right=0.9, top=0.9)
    plt.savefig('static/result_image.png', format='png')


class DataSource:
    """
    DataSource executes all of the queries on the database.
    It also formats the data to send back to the frontend, typically in a list
    or some other collection or object.
    """

    def __init__(self):
        """
        Constructor for the datasource, just opens a database connection.
        """
        # Connect to the database
        try:
            self.connection = psycopg2.connect(database=psqlConfig.database, user=psqlConfig.user,
                                          password=psqlConfig.password, host="localhost")
        except Exception as e:
            print("Connection error: ", e)
            exit()
    
    def _get_number_of_avg_players_in_range(self, game_title, start, end):
        """
        A helper method that returns a list of the average player numbers for every month from the specified starting
        month & year until the specified ending month & year for the specified game title
        
        Parameters:
            game_title - a string of the name of the game
            start - first datetime object where the range starts
            end - last datetime object that should be in the set
        
        Returns:
            a list of game objects in chronological order for every month from the start to the end month 
        """
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM compareGames WHERE (gameDate::date BETWEEN %s AND %s) AND gameTitle = %s"
            cursor.execute(query, (start, end, game_title,))
            return_list = cursor.fetchall()
            return_list = _list_of_game_objects(return_list)
            return_list = _fill_out_data(return_list, start, end)
            return return_list

        except Exception as e:
            print("Something went wrong when executing the query: ", e)
            return None

    def list_compare_avg_players_in_range(self, game1_title, game2_title, start_year, start_month, end_year, end_month):
        """
        Returns two lists, one for each game title, that has the average player number for each month in the specified
        time range
        
        Parameters:
            game1_title - a string of the name of the first game
            game2_title - a string of the name of the second game
            start_year - a string of the year where the data should start being collected from
            start_month - a string of the month where the data should start being collected from
            end_year - a string of the last year to collect data from
            end_month - a string of the month to stop collected data from
        
        Returns:
            two lists, one for each game in chronological order, of the average number of players on Steam playing that
            game in each month in the time range given. These are then graphed
        """
        start = _to_datetime(start_year, start_month)
        end = _to_datetime(end_year, end_month)
        game1_list = self._get_number_of_avg_players_in_range(game1_title, start, end)
        game2_list = self._get_number_of_avg_players_in_range(game2_title, start, end)
        _save_graph(game1_list, game2_list)
        return game1_list, game2_list
    
    def list_monthly_top_games(self, year, month):
        """
        Returns a list of the top games by peak player count on Steam for the specified month. The game
        with the highest number of players playing simultaneously during that month is first, and then 
        the rest of the 100 top games on Steam follow in decreasing order. 
        
        Parameters:
            year - a string that has the year of interest
            month - a string that has the month of interest
       
       Return:
            a list of the most popular games on Steam for that month
        """
        try:
            selected_date = _to_datetime(year, month)
            cursor = self.connection.cursor()
            query = "SELECT gameTitle FROM topGames WHERE gameDate = %s ORDER BY peakPlayers DESC"
            cursor.execute(query, (selected_date,))
            return_list = cursor.fetchall()
            return return_list

        except Exception as e:
            print("Something went wrong when executing the query: ", e)
            return None
    
    def list_popularity_over_all_time(self, game_title):
        """
        Returns a list of the monthly average player count on Steam for every month in the dataset for the game_title, 
        with zeros whenever the game did not reach the top 100 games on Steam

        Parameters:
            game_title - the string game title of the game of interest

        Return:
            a list of the monthly average player count for every month in the dataset for the specified game title
        """
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM comparegames WHERE gametitle = %s"
            cursor.execute(query, (game_title,))
            returned_list = cursor.fetchall()
            start_date = _to_datetime('2012', '7')
            end_date = _to_datetime('2021', '9')
            returned_list = _list_of_game_objects(returned_list)
            returned_list = _fill_out_data(returned_list, start_date, end_date)
            return_list = []
            for g in returned_list:
                return_list.append([g.get_title(), g.get_date(), g.get_stats()])
            return return_list

        except Exception as e:
            print("Something went wrong when executing the query: ", e)
        return None

    
def main():
    # what is the average player number for these two games over this time frame?
    datasource = DataSource()
    results = datasource.list_popularity_over_all_time('Dota 2')
    result_compare_games = datasource.list_compare_avg_players_in_range('Dota 2', 'Rust', "2018", "11", "2019", "04")
    result_monthly_top = datasource.list_monthly_top_games("2014", "10")
    if results is not None:
        print("Popularity Graph All Time Query results: ")
        for item in results:
            print(item)
    if result_compare_games is not None:
        print("compare games results: ")
        for item in result_compare_games:
            print(item)
    if result_monthly_top is not None:
        print("Monthly Top Games results: ")
        for item in result_monthly_top:
            print(item)
    # Disconnect from database
    datasource.connection.close()

if __name__ =="__main__":
    main()
