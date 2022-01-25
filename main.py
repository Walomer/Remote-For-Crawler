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
    #! Gerer les required sur le champ du form pour que request.form ait toujours la meme taille
    print(request.form.to_dict(flat=False))
    typeSearch = list(request.form.to_dict(flat=False).keys())[1]
    search = request.form.get('search')

    tweets = []
    if typeSearch == "typeUsers":
        scraper = twitterScraper.TwitterUserScraper("KermitTheFrog", False)
        for i, tweet in enumerate(scraper.get_items()):
            tweets.append({"id": tweet.id, "user": tweet.user, "content": tweet.content,
                          "reply": tweet.replyCount, "retweet": tweet.retweetCount,
                           "likes": tweet.likeCount, "langue": tweet.lang, "date": tweet.date})
        msg = search+" by users"
    elif typeSearch == "typeHashtag":
        # twitterScraper.TwitterHashtagScraper()
        msg = search+" by #"
    else:
        # twitterScraper.TwitterSearchScraper()
        msg = search+" a determiner"
    return render_template('home.html', toprint=msg)


def get_db_connection():
    conn = sqlite3.connect('database/database.db')
    conn.row_factory = sqlite3.Row
    return conn


if __name__ == "__main__":
    app.run(debug=True, port=3000)
