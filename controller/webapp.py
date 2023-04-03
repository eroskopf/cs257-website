'''
our webapp for our website 
'''

import flask
from flask import render_template, request
import json
import sys
import datasource

app = flask.Flask(__name__)

# This line tells the web browser to *not* cache any of the files.
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/table_results', methods=['POST', 'GET'])
def tableResult():
    '''
    This method is executed once you submit the simple form. It embeds the form responses
    into a web page.
    '''
    if request.method == 'POST':
        top_month = request.form["month"]
        top_year = request.form["year"]

        model = datasource.DataSource()
        stats = model.list_monthly_top_games(top_year, top_month)

    return render_template('table_results.html', results=stats, month=top_month, year=top_year)
        # Here is where you would call one or more database methods with the form data.

@app.route('/graph_results', methods=['POST', 'GET'])
def graphResults():
    '''
    This method is executed once the first form on the homepage is submitted. It embeds the
    form responses into a web page and generates a graph
    '''
    if request.method == 'POST':
        start_month = request.form["start_month"]
        start_year = request.form["start_year"]
        end_month = request.form["end_month"]
        end_year = request.form["end_year"]
        game_one = request.form["game_name_1"]
        game_two = request.form["game_name_2"]
        
        model = datasource.DataSource()
        
        try:
            stats = model.list_compare_avg_players_in_range(game_one, game_two, start_year, start_month, end_year, end_month)
        except Exception as e:
            return render_template('null_result.html')
    

    return render_template('graph_results.html', results=stats, game_name_1=game_one, game_name_2=game_two, 
                           start_month_num=start_month, end_month_num=end_month, start_year_num=start_year,
                          end_year_num=end_year)

 
@app.route('/one_line_graph', methods=['POST', 'GET'])
def oneLineGraph():
    '''
    This method is executed once the first form on the homepage is submitted. It embeds the
    form responses into a web page and generates a graph, with just one line
    '''
    if request.method == 'POST':
        game_title = request.form["game_name"]
        
        model = datasource.DataSource()
        stats = model.list_popularity_over_all_time(game_title)

        if stats == None:
            return render_template('null_result.html')
        
    return render_template('one_line_graph_results.html', game_name=game_title)
    
@app.errorhandler(404)
def page_not_found(e):
    '''
    This method redirects the user to an error page if the user's queries are faulty or incompatible with the dataset.
    '''
    return render_template('null_result.html'), 404

@app.route('/')
def openHomePage():
    '''
    This method opens the home page.
    '''
    return render_template('home_page.html')

@app.route('/about')
def openAboutPage():
    '''
    This method opens the about page.
    '''
    return render_template('about.html')

@app.route('/topgames')
def openTopGamesPage():
    '''
    This method opens the top games page.
    '''
    model = datasource.DataSource()
    stats = model.list_all_top_games()
    
    return render_template('topgames.html', results=stats)

'''
Run the program by typing 'python3 localhost [port]', where [port] is one of 
the port numbers you were sent by my earlier this term.
'''
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: {0} host port'.format(sys.argv[0]), file=sys.stderr)
        exit()

    host = sys.argv[1]
    port = sys.argv[2]
    app.run(host=host, port=port)

