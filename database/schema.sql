DROP TABLE IF EXISTS posts;

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_date TIMESTAMP NOT NULL,
    command_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tweet_id INTEGER UNIQUE NOT NULL ,
    reply_count INTEGER,
    retweet_count INTEGER,
    lang TEXT,
    user_name TEXT NOT NULL,
    content TEXT NOT NULL,
    likes INTEGER,
    search TEXT NOT NULL,
    linkToTweet TEXT NOT NULL,
    id_requete INTEGER NOT NULL
);

CREATE TABLE requetes (
    id INTEGER PRIMARY KEY,
    nom_recherche TEXT NOT NULL,
    type TEXT NOT NULL,
    date TIMESTAMP NOT NULL,
    quantite INTEGER NOT NULL
);