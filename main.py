import sqlite3
from werkzeug.exceptions import abort
from flask import Flask, render_template, request
import sys
import snscrape.modules.twitter as twitterScraper

app = Flask(__name__)


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

    # Des qu'on arrive à la qte demandé, on s'arrete
    if qte != 0:
        for i, tweet in enumerate(scraper.get_items()):
            tweets.append({"id": tweet.id, "user": tweet.user.username, "content": tweet.content,
                          "reply": tweet.replyCount, "retweet": tweet.retweetCount,
            if i > qte:
                break
            tweets.append({"id": tweet.id, "user": tweet.user.username, "content": tweet.content,
                           "reply": tweet.replyCount, "retweet": tweet.retweetCount,
                           "likes": tweet.likeCount, "langue": tweet.lang, "date": tweet.date})
        ####  Ajout dans la base de donnée de chaques réponses ###
            #Préparation de la requête
            sqlite_insert_query = "INSERT INTO posts (tweet_id, user_name, content, reply_count, retweet_count, likes, created) VALUES (" + str(tweet.id) + "," + str(tweet.user.username) + "," + str(tweet.content) + "," + str(tweet.replyCount) + "," + str(tweet.retweetCount) + "," + str(tweet.likeCount) + "," + str(tweet.date) + ")"
            # print(sqlite_insert_query)
            sqliteConnection.execute("""INSERT INTO posts (tweet_id, user_name, content, reply_count, retweet_count, likes, created_date) 
                    VALUES (?,?,?,?,?,?,?);""", (tweet.id, tweet.user.username, tweet.content, tweet.replyCount, tweet.retweetCount, tweet.likeCount, tweet.date))
            print("Record inserted successfully into SqliteDb_developers table ")

        msg = search+" by users"
    elif typeSearch == "typeHashtag":
        # twitterScraper.TwitterHashtagScraper()
        msg = search+" by #"
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
        # twitterScraper.TwitterSearchScraper()
        msg = search+" a determiner"

    sqliteConnection.commit()
    posts = cursor.execute('SELECT * FROM posts').fetchall()
    print(posts)
    cursor.close()
    return render_template('home.html', toprint=msg, posts=posts)


def get_db_connection():
    conn = sqlite3.connect('database/database.db')
    conn.row_factory = sqlite3.Row
    return conn


if __name__ == "__main__":
    app.run(debug=True, port=3000)
