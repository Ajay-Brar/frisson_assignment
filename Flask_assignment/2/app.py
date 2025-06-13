from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def hello_world():
    return '<p> to go to the next page type /1 for other page inside URL to come back to tthis page give only / part in URL'

@app.route("/1")
def next():
    return render_template("index.html")


if __name__ == '__main__':
    app.run()

