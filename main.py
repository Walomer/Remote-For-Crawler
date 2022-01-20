import sqlite3
from werkzeug.exceptions import abort
from flask import Flask, render_template, request
import sys

app = Flask(__name__)


@app.route('/')
def home():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('home.html', posts=posts)


@app.route('/research', methods=['GET'])
def research():
    return render_template('home.html')
#     if request.args.get('search'):
#         return render_template('home.html', query=query, research=word, ask=ans)
#     else:
#         return render_template('home.html')

def get_db_connection():
    conn = sqlite3.connect('database/database.db')
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == "__main__":
    app.run(debug=True, port=3000)
