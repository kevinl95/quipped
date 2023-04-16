import random
from flask import Flask, render_template, send_file, request, jsonify
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
        elif letter == "?":
            word.pop()
        elif letter in word:
            word.remove(letter)

    return len(word) == 0


## Constant letter point values
class letterValue:
  values = [['?'], 
            ['A','E','I','L','N','O','R','S','T','U'],
            ['D','G'],
            ['B','C','M','P'],
            ['F','H','V','W','Y'],
            ['K'],
            [],
            [],
            ['J','X'],
            [],
            ['Q','Z']];

class tempMemory:
  def __init__(self):
    self.storedLetters = []
    self.scannedLetters = []

def getLetterValue(letter):
  for value in letterValue.values:
    if letter.upper() in letterValue.values[letterValue.values.index(value)]:
      return letterValue.values.index(value);
  raise Exception('Argument is NOT a valid Scrabble letter.');

def getWordValue(word):
  finalValue = 0;
  for char in word:
    finalValue += getLetterValue(char);
  return finalValue;


def create_app():
    app = Flask(__name__)
    PWA(app)

    @app.route("/checkword", methods=["POST"])
    def receive_data():
        userInput = request.form["word"].upper()  # Convert to uppercase
        response = "True"
        score = 0
        rack = request.form["rack"]
        if len(userInput) > 7 or not userInput.isalpha():
            response = "Invalid"
        if response != "Invalid":
            letters = rack
            result = []
            with open("dictionary.txt", "r") as words_file:
                for line in words_file:
                    word = line.strip()
                    if can_spell(letters, word):
                        result.append(word)
            result = sorted(result, key=lambda w: len(w), reverse=True)
            if userInput not in result:
                response = "False"
            else:
                score = getWordValue(userInput)
        toReturn = {"return": response, "score" : score}
        return jsonify(toReturn)

    @app.route("/")
    def index():
        # Creating a datetime object for tday
        a = datetime.now()

        # Converting a to string in the desired format (YYYYMMDD) using strftime
        # and then to int.
        a = int(a.strftime("%Y%m%d"))
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
        with open("dictionary.txt", "r") as words_file:
            for line in words_file:
                word = line.strip()
                if can_spell(letters, word):
                    result.append(word)
        result = sorted(result, key=lambda w: len(w), reverse=True)
        if len(result) == 0:
            newres = []
            ind = 100000
            # Loop until we have a valid rack
            while len(newres) == 0:
                a = a + ind
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
                with open("dictionary.txt", "r") as words_file:
                    for line in words_file:
                        word = line.strip()
                        if can_spell(letters, word):
                            result.append(word)
                newres = sorted(result, key=lambda w: len(w), reverse=True)
                ind = ind + 1
        return render_template("index.html", rack=prettyRack)

    return app
