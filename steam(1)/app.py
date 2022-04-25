'''
Python 3
Software Engineering
Written By: Nadia Morrow
Date Last Updated: 24/04/2024
This program creates the routes between the webpages and connects the algorithm to the web application.
'''

#importing neccessary libraries
from codecs import StreamReader
from operator import index
from re import A, template
from flask import Flask, render_template, request, g, session, flash, redirect, abort
import pandas as pd
import algorithm
from pysteamsignin.steamsignin import SteamSignIn
import os, sys
from steam.webapi import WebAPI
import json
import collections

#creating the web application
app = Flask(__name__, template_folder='templates')

#Creating the route to the home page 
@app.route("/")
def home():
    return render_template("/welcomePlus/index.html")

#created the route for the manual page
@app.route("/manualLogin", methods=['POST', 'GET'])
def manualLogin():
    #checks if the web page is asking and if so provides the list of games as an imput
    if request.method == 'GET':
        Game = ['Football Manager 2012', 'Football Manager 2014', 'Counter-Strike Global Offensive', 'Football Manager 2013', 'Dota 2', 'Football Manager 2015', "Sid Meier's Civilization V", 'Counter-Strike', 'Arma 3', 'Mount & Blade Warband', 'The Elder Scrolls V Skyrim', 'Grand Theft Auto V', 'Empire Total War', 'Total War SHOGUN 2', 'ARK Survival Evolved', 'Rust', 'Terraria', 'Fallout 4', 'The Binding of Isaac Rebirth', 'Borderlands 2', 'PAYDAY 2', 'Napoleon Total War', 'Fallout New Vegas', 'The Witcher 3 Wild Hunt', 'Battlefield Bad Company 2', 'H1Z1', 'Rocket League', 'Left 4 Dead 2', 'XCOM Enemy Unknown', 'Killing Floor', 'Warframe', 'Dark Souls Prepare to Die Edition', 'Left 4 Dead', 'Call of Duty Modern Warfare 2', 'Portal 2', 'Grand Theft Auto IV']
        return render_template(r"register-19.html", game = Game)
    #checks if the web page is sending information and takes the information to put into the algorithm to recieve the recommendation then sends user to results page
    if request.method == 'POST':
        game = request.form.get("games")
        if game != None:
            print(game)
            pred = algorithm.getUserInput(game)
            g1 = pred[0]
            g2 = pred[1]
        else:
            print("game is empty")
        return render_template('results.html', game1 = g1, game2 = g2)

#routes to the api login page
@app.route("/apiLogin")
def apiLogin():
    return render_template(r"login-19.html")

#routes to the steam website to get user information
@app.route("/login")
def steamLogin():
    steamLogin = SteamSignIn()
    return(steamLogin.RedirectUser(steamLogin.ConstructURL('https://localhost:8080/processlogin')))

#intermediate page that gets the data from the steam page, calls the api and gets the user top game then sends it to the algorithm to get recommendation games
@app.route("/processlogin")
def process():
    returnData = request.values   
    steamLogin = SteamSignIn()
    steamID = steamLogin.ValidateResults(returnData) #ensures that the information came back properly
    print('SteamID returned is: ', steamID)
    Game = ['Football Manager 2012', 'Football Manager 2014', 'Counter-Strike Global Offensive', 'Football Manager 2013', 'Dota 2', 'Football Manager 2015', "Sid Meier's Civilization V", 'Counter-Strike', 'Arma 3', 'Mount & Blade Warband', 'The Elder Scrolls V Skyrim', 'Grand Theft Auto V', 'Empire Total War', 'Total War SHOGUN 2', 'ARK Survival Evolved', 'Rust', 'Terraria', 'Fallout 4', 'The Binding of Isaac Rebirth', 'Borderlands 2', 'PAYDAY 2', 'Napoleon Total War', 'Fallout New Vegas', 'The Witcher 3 Wild Hunt', 'Battlefield Bad Company 2', 'H1Z1', 'Rocket League', 'Left 4 Dead 2', 'XCOM Enemy Unknown', 'Killing Floor', 'Warframe', 'Dark Souls Prepare to Die Edition', 'Left 4 Dead', 'Call of Duty Modern Warfare 2', 'Portal 2', 'Grand Theft Auto IV']
    api = WebAPI(key="D2161D6E2E2A13C22B412FD5E158DE52")
    #checks to make sure there is actually an input in steamID
    if steamID is not False:
        #calling the api
        games = api.IPlayerService.GetOwnedGames(steamid=steamID, include_appinfo=True,include_played_free_games=True, appids_filter=False, include_free_sub=True)
        game1 = games.get('response')
        finalGame = game1.get('games')
        #checks if the user's steam account can be used with the api
        if finalGame is not None:
            gamePlaytime = {}
            #loop to create a dictionary with the user's games and their playtime 
            for game in finalGame:
                gamePlaytime.update({game.get('name'): game.get('playtime_forever')})
            #sorting the dictonary so that the most played games are first
            sorted_list = sorted(gamePlaytime.items(), key=lambda x: x[1], reverse=True)
            finalDict = collections.OrderedDict(sorted_list)
            #loop to find the most played game that is in our dataset 
            for a in finalDict:
                if a in Game:
                  userGame = a
                  break
            #using the found game and calling the algorithm to get prediction
            pred = algorithm.getUserInput(userGame)
            g1 = pred[0]
            g2 = pred[1]
            #returning the recommend games to the results page and sending user there
            return render_template("results.html", game1=g1, game2=g2)
        else:
            #if the account is inelgible, send the user to input manually their game
            return redirect('manualLogin')
    else:
        #if login fails, send user to api page to try again
        return redirect('/apiLogin')

#routing to rating explaination page
@app.route("/ratings")
def ratings():
    #getting the top games and their scores from the algorithm and sending the information to the page
    topGames = algorithm.getTopGames()
    tG1 = topGames[0]
    tG2 = topGames[1]
    tG3 = topGames[2]
    sG1 = topGames[3]
    sG2 = topGames[4]
    sG3 = topGames[5]
    return render_template(r"/welcomePlus/ratings.html", topGame1 = tG1, topGame2 = tG2, topGame3 = tG3, sumGame1 = sG1, sumGame2 = sG2, sumGame3 = sG3)

#routing to the feedback page
@app.route("/feedback")
def feedback():
    return render_template(r"/welcomePlus/feedbacks.html")

#parameters for runnign the web application 
if __name__ == "__main__":
    app.secret_key = 'super secret key'
    os.environ['Flask_ENV'] = 'development'
    app.run(host='localhost', port = 8080, ssl_context='adhoc', debug=False)