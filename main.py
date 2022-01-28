from nis import match
import sqlite3
from werkzeug.exceptions import abort
from flask import Flask, render_template, request
import sys
import snscrape.modules.twitter as twitterScraper

app = Flask(__name__)

# Liste des tweets que l'on va recuperer -> JSON file
tweets = []


@app.route('/')
def home():
    # conn = get_db_connection()
    # posts = conn.execute('SELECT * FROM posts').fetchall()
    # conn.close()
    return render_template('home.html')  # , posts=posts)


@app.route('/research', methods=['POST'])
def research():
    #! afficher les tweet dans article selon bdd
    #! regarder si possibilite de stop, reprendre, 10 avant, 10 apres (la télécommande)
    # ? Meiller facon pour refresh c'est de call AJAX. fonction avec timer sur notre JSON et on recup le res de al taille

    print(request.form.to_dict(flat=False))
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

    # Des qu'on arrive à la qte demandé, on s'arrete
    if qte != 0:
        for i, tweet in enumerate(scraper.get_items()):
            if i > qte:
                break
            tweets.append({"id": tweet.id, "user": tweet.user.username, "content": tweet.content,
                           "reply": tweet.replyCount, "retweet": tweet.retweetCount,
                           "likes": tweet.likeCount, "langue": tweet.lang, "date": tweet.date})
    # Pas de qte donne, on prends donc tout les tweet correspodant
    else:
        for i, tweet in enumerate(scraper.get_items()):
            tweets.append({"id": tweet.id, "user": tweet.user.username, "content": tweet.content,
                           "reply": tweet.replyCount, "retweet": tweet.retweetCount,
                           "likes": tweet.likeCount, "langue": tweet.lang, "date": tweet.date})

    # * Ici on ajoute dans la BD
    #! Formatter la date en yyyy-mm-jj => split " " ; [0]

    # print(tweets)
    return render_template('home.html', ans=tweets)


def get_db_connection():
    conn = sqlite3.connect('database/database.db')
    conn.row_factory = sqlite3.Row
    return conn


if __name__ == "__main__":
    app.run(debug=True, port=3000)
