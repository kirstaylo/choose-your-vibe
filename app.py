''' tutorials used to build this app:
https://towardsdatascience.com/an-interactive-web-dashboard-with-plotly-and-flask-c365cdec5e3f
https://towardsdatascience.com/create-and-deploy-a-simple-web-application-with-flask-and-heroku-103d867298eb
'''

import pandas as pd
import numpy as np
import json
import plotly
import plotly.express as px
from scipy.spatial import distance
from flask import Flask, render_template, request, redirect

# instantiate the app
app = Flask(__name__, template_folder='./templates')

# read the experiment data
siot_data = pd.read_csv('./siot_data.csv')
plots = {'x':'energy',
        'y': 'EDA'}

# read the song feature space
songs = pd.read_csv('./song_db.csv')
features = songs[['energy', 'valence', 'danceability', 'acousticness']]
features = np.matrix(features)

fig1 = px.scatter_3d(songs, x='danceability', y='acousticness', z='valence', color='energy')
songs_graphJSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

# find the closest song for the submitted audio features
def closest_node(node, nodes):
    closest_index = distance.cdist([node], nodes).argmin()
    return closest_index

# pick the chosen song from the dataframe
def choose_song(energy, valence, danceability, acousticness):
    chosen_pt = (int(energy)/100, int(valence)/100, int(danceability)/100, int(acousticness)/100)
    i = closest_node(chosen_pt, features)
    url = str(songs[['url']].iloc[i]['url'])
    if url=="nan":
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    name = songs[['name']].iloc[i]['name']
    artist = songs[['artist']].iloc[i]['artist']
    genre = songs[['genre']].iloc[i]['genre']
    song_str = "{} by {} (genre: {})".format(name, artist, genre)
    return song_str, url

# make the experiment data graph
def build_graph(x="energy", y="EDA"):
    fig = px.scatter(siot_data, x=x, y=y)
    siot_graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return siot_graphJSON

# update features of experiment data graph
@app.route('/graph', methods=['POST'])
def graph():
    plots['x'] = request.form["x-var"]
    plots['y'] = request.form["y-var"]
    return redirect(request.referrer)

@app.route("/")
def index():
    return render_template("index.html", song_str='No current song', url="https://www.youtube.com/watch?v=dQw4w9WgXcQ", 
                           songs_graphJSON=songs_graphJSON, siot_graphJSON=build_graph(plots['x'], plots['y']))

@app.route('/', methods=['POST'])
def search_song():
    energy = request.form["EnergyRange"]
    valence = request.form["ValenceRange"]
    danceability = request.form["DanceabilityRange"]
    acousticness = request.form["AcousticnessRange"]

    # choose new song based on submitted features
    song_str, url = choose_song(energy, valence, danceability, acousticness)
    return render_template("index.html", song_str=song_str, url=url, songs_graphJSON=songs_graphJSON,  siot_graphJSON=build_graph(plots['x'], plots['y']))

if __name__ == "__main__":
    app.run()