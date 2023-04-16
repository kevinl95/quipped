import random
from flask import Flask, render_template, send_file
from flask_pwa import PWA
from scrabble.main import ScrabbleGame
from datetime import datetime

# Monkeypatching PWA implementation

def init_sw(self):
    return send_file(
        "static/js/sw.js",
        attachment_filename="sw.js",
    )

def init_manifest(self):
    return send_file(
        "static/manifest.json",
        attachment_filename="manifest.json",
    )

PWA._init_sw = init_sw
PWA._init_manifest = init_manifest

def can_spell(letters, word):
    # reverse sort to get the blanks ('?') to the end of letters string,
    # so that the greedy algorithm works
    letters = sorted(letters, reverse=True)
    word = list(word)

    for letter in letters:
        if len(word) == 0:
            return True
        elif letter == '?':
            word.pop()
        elif letter in word:
            word.remove(letter)

    return len(word) == 0

def create_app():
    app = Flask(__name__)
    PWA(app)

    @app.route('/background_process_test')
    def background_process_test():
        print ("Hello")
        return ("nothing")

    @app.route("/")
    def index():
        # Creating a datetime object for tday
        a = datetime.now()

        # Converting a to string in the desired format (YYYYMMDD) using strftime
        # and then to int.
        a = int(a.strftime('%Y%m%d'))
        # Use as our seed so everyone gets the same rack
        random.seed(a)
        game = ScrabbleGame(num_players=1)
        r = game.player_rack_list[0]
        prettyRack = ""
        for l in r:
            if l.letter == "*":
                prettyRack += "?"
            else:
                prettyRack += l.letter
        letters = prettyRack

        result = []
        with open('dictionary.txt', 'r') as words_file:
            for line in words_file:
                word = line.strip()
                if can_spell(letters, word):
                    result.append(word)

        result = sorted(result, key=lambda w: len(w), reverse=True)
        return render_template("index.html", rack=prettyRack)

    return app
