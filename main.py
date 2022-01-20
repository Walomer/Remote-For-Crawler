from flask import Flask, render_template, request
import sys

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/research', methods=['GET'])
def research():
    return render_template('home.html')
#     if request.args.get('search'):
#         return render_template('home.html', query=query, research=word, ask=ans)
#     else:
#         return render_template('home.html')


if __name__ == "__main__":
    app.run(debug=True, port=3000)
