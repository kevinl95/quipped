from flask import Flask, render_template, send_file
from flask_pwa import PWA

# Monkeypatching PWA implementation

def init_sw(self):
    print("I got used")
    return send_file(
        "static/js/sw.js",
        attachment_filename="sw.js",
    )

def init_manifest(self):
    print("And I got used")
    return send_file(
        "static/manifest.json",
        attachment_filename="manifest.json",
    )

PWA._init_sw = init_sw
PWA._init_manifest = init_manifest

def create_app():
    app = Flask(__name__)
    PWA(app)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app
