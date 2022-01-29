import sqlite3
from werkzeug.exceptions import abort
from flask import Flask, render_template, request
import sys
import snscrape.modules.twitter as twitterScraper

app = Flask(__name__)

@app.route('/')
def home():
    #connection à la base de donnée
    sqliteConnection  = sqlite3.connect('database/database.db')
    cursor = sqliteConnection.cursor()
    posts = cursor.execute('SELECT * FROM posts').fetchall()
    cursor.close()
    return render_template('home.html', posts=posts)

@app.route('/research', methods=['POST'])
def research():
    print(request.form.to_dict(flat=False))

    #connection à la base de donnée
    sqliteConnection  = sqlite3.connect('database/database.db')
    cursor = sqliteConnection.cursor()

    typeSearch = list(request.form.to_dict(flat=False).keys())[1]
    search = request.form.get('search')
    typeSearch = request.form.get('typeRecherche')
    qte = request.form.get('qte_tweet')

    # Si on arrive ici, c'est un nouvelle recherche, dont on réinitialise notre liste
    tweets = []

    # On filtre selon le form
    if typeSearch == "typeUsers":
        scraper = twitterScraper.TwitterUserScraper(search, False)
    elif typeSearch == "typeHashtag":
        scraper = twitterScraper.TwitterHashtagScraper(search)
    else:
        scraper = twitterScraper.TwitterSearchScraper(search)

    #On vérifie que la quantité choisie n'est pas 0 pour pouvoir choisir le nombre de tweet que l'on veut
    if qte != 0:
        for i, tweet in enumerate(scraper.get_items()):
            # On regarde le nombre demander dans le formulaire et une fois qu'on arrive à cette quantité on sort de la boucle
            if i > int(qte):
                break
            ajoutBDD(tweet,search)

    # Pas de qte donne, on prends donc tout les tweet correspodant
    else:
        # On parcours la liste des résultat du scrap pour les ajouter dans un dictionnaire afin de pouvoir traiter les données plus facilement
        for i, tweet in enumerate(scraper.get_items()):
            ajoutBDD(tweet,search)

    # On récupère toute les donnée de la base de donnée afin de les afficher sur le résultat
    posts = cursor.execute('SELECT * FROM posts').fetchall()
    # On ferme la lecture/écriture à la base de donnée
    cursor.close()
    return render_template('home.html', posts=posts)


def get_db_connection():
    conn = sqlite3.connect('database/database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Ajoutes les données dans la base de donnée
def ajoutBDD(tweet, search):
    sqliteConnection  = sqlite3.connect('database/database.db')
    cursor = sqliteConnection.cursor()
    print("lien twiter : " + str(tweet))
    # Recherche des tweet_id afin d'éviter les doublons
    tweets_id = cursor.execute('SELECT tweet_id FROM posts').fetchall()
    # Vérification qu'il existe déjà une valeur dans la base de donnée sinon on ne pourra pas parcourir les tweet pour vérifier
    if(tweets_id):
        for tweet_id in tweets_id[0]:
            # Vérification pour ne pas ajouter les doublons et ne pas avoir de problème avec la base de donnée
            if tweet_id != tweet.id:
                ####  Ajout dans la base de donnée de chaques réponses ###
                # Préparation de la requête
                sqliteConnection.execute("""INSERT INTO posts (tweet_id, user_name, content, reply_count, retweet_count, likes, created_date, search, linkToTweet) 
                                       VALUES (?,?,?,?,?,?,?,?,?);""", (
                    tweet.id, tweet.user.username, tweet.content, tweet.replyCount, tweet.retweetCount, tweet.likeCount,
                    tweet.date, search, str(tweet)))
                print("Record inserted successfully into SqliteDb_developers table ")
    # Si il n'y a rien le premier tweet sera l'initialisation de notre base de donnée
    else:
        sqliteConnection.execute("""INSERT INTO posts (tweet_id, user_name, content, reply_count, retweet_count, likes, created_date, search, linkToTweet) 
                               VALUES (?,?,?,?,?,?,?,?,?);""", (
            tweet.id, tweet.user.username, tweet.content, tweet.replyCount, tweet.retweetCount, tweet.likeCount,
            tweet.date, search, str(tweet)))
    sqliteConnection.commit()

if __name__ == "__main__":
    app.run(debug=True, port=3000)
