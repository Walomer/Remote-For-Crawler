import datetime
import sqlite3
from flask import Flask, render_template, request
import snscrape.modules.twitter as twitterScraper

pause = False
app = Flask(__name__)
tweets = []


@app.route('/')
def home():
    # connection à la base de donnée
    sqliteConnection = sqlite3.connect('database/database.db')
    cursor = sqliteConnection.cursor()
    posts = cursor.execute('SELECT * FROM posts').fetchall()
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    requete = cursor.execute('SELECT * FROM requetes').fetchall()
    # Verification du numero de requete
    if (not requete):
        # Si vide, on init à 0
        id_rq = 0
    else:
        # On prend la dernier element ([-1]), son id [0], et on ajoute 1
        id_rq = requete[-1][0] + 1
    cursor.close()
    return render_template('home.html', posts=posts, id_requete=id_rq)


@app.route('/research', methods=['POST'])
def research():

    # ! regarder si possibilite de stop, reprendre, 10 avant, 10 apres (la télécommande)
    # ! Gestion des bouttons de la telecommande ici !! Selon des fonctions definies et des variables globales
    # Connection à la base de donnée
    sqliteConnection = sqlite3.connect('database/database.db')
    cursor = sqliteConnection.cursor()

    # Voir les parametres du form
    # print(request.form.to_dict(flat=False))

    # On récupère le numéro de la requete
    id_requete = request.form.get("id_requete")
    # On recupere les parametre important: recherche / type / qte
    typeSearch = list(request.form.to_dict(flat=False).keys())[1]
    search = request.form.get('search')
    typeSearch = request.form.get('typeRecherche')
    qte = request.form.get('qte_tweet')

    # On filtre selon le type de recherche
    if typeSearch == "typeUsers":
        scraper = twitterScraper.TwitterUserScraper(search, False)
    elif typeSearch == "typeHashtag":
        scraper = twitterScraper.TwitterHashtagScraper(search)
    else:
        scraper = twitterScraper.TwitterSearchScraper(search)

    # On vérifie que la quantité choisie n'est pas 0 pour pouvoir choisir le nombre de tweet que l'on veut
    if qte != 0:
        for i, tweet in enumerate(scraper.get_items()):
            # On regarde le nombre demander dans le formulaire et une fois qu'on arrive à cette quantité on sort de la boucle
            if i > int(qte):
                break
            ajoutBDD(tweet, search, id_requete)
    # Pas de qte donne, on prends donc tout les tweet correspodant
    else:
        # On parcours la liste des résultat du scrap pour les ajouter dans un dictionnaire afin de pouvoir traiter les données plus facilement
        for i, tweet in enumerate(scraper.get_items()):
            ajoutBDD(tweet, search, id_requete)

    # On récupère toute les donnée de la base de donnée afin de les afficher sur le résultat
    posts = cursor.execute('SELECT * FROM posts').fetchall()

    # Ajout de la nouvelle requete à la base de donnée
    sqliteConnection.execute("""INSERT INTO requetes (id, nom_recherche, type, date, quantite)
                            VALUES (?,?,?,?,?);""", (
        id_requete, search, typeSearch, datetime.datetime.now().date(), qte))

    # On récupère toute les donnée de la base de donnée afin de les afficher sur le résultat
    requete = cursor.execute('SELECT * FROM requetes').fetchall()
    sqliteConnection.commit()

    # On ferme la lecture/écriture à la base de donnée
    cursor.close()
    # On revoit sur la page home avec un id+1 pour eviter les doublons / erreurs
    return render_template('home.html', posts=posts, id_requete=int(id_requete)+1)


def get_db_connection():
    conn = sqlite3.connect('database/database.db')
    conn.row_factory = sqlite3.Row
    return conn


# Ajoutes les données dans la base de donnée
def ajoutBDD(tweet, search, id_requete):
    sqliteConnection = sqlite3.connect('database/database.db')
    cursor = sqliteConnection.cursor()
    print("lien twiter : " + str(tweet))
    # Recherche des tweet_id afin d'éviter les doublons
    tweets_id = cursor.execute('SELECT tweet_id FROM posts').fetchall()
    # Vérification qu'il existe déjà une valeur dans la base de donnée sinon on ne pourra pas parcourir les tweet pour vérifier
    if (tweets_id):
        if (checkIfTweetExist(tweet.id)):
            # Vérification pour ne pas ajouter les doublons et ne pas avoir de problème avec la base de donnée
            ####  Ajout dans la base de donnée de chaques réponses ###
            # Préparation de la requête
            sqliteConnection.execute("""INSERT INTO posts (tweet_id, user_name, content, reply_count, retweet_count, likes, created_date, search, linkToTweet, id_requete) 
                                   VALUES (?,?,?,?,?,?,?,?,?,?);""", (
                tweet.id, tweet.user.username, tweet.content, tweet.replyCount, tweet.retweetCount, tweet.likeCount,
                tweet.date, search, str(tweet), id_requete))
            print("Record inserted successfully into SqliteDb_developers table ")
    # Si il n'y a rien le premier tweet sera l'initialisation de notre base de donnée
    else:
        sqliteConnection.execute("""INSERT INTO posts (tweet_id, user_name, content, reply_count, retweet_count, likes, created_date, search, linkToTweet, id_requete) 
                               VALUES (?,?,?,?,?,?,?,?,?,?);""", (
            tweet.id, tweet.user.username, tweet.content, tweet.replyCount, tweet.retweetCount, tweet.likeCount,
            tweet.date, search, str(tweet), id_requete))
    sqliteConnection.commit()


# Regarde si le tweet est déjà dans la base de donné
def checkIfTweetExist(tweetidToAdd):
    exist = True
    sqliteConnection = sqlite3.connect('database/database.db')
    cursor = sqliteConnection.cursor()
    tweets_id = cursor.execute('SELECT tweet_id FROM posts').fetchall()
    for tweet_id in tweets_id:
        print("ID Tweet déjà enregistrer " + str(tweet_id))
        print("ID à vérifier " + str(tweetidToAdd))
        if (tweetidToAdd == tweet_id[0]):
            exist = False
            break
    print(exist)
    return exist

@app.route('/changePauseSetting')
def changePauseSetting():
    global pause
    if(pause):
        pause =False
    else:
        pause = True
    print(pause)
    return render_template('home.html')


if __name__ == "__main__":
    app.run(debug=True, port=3000)
