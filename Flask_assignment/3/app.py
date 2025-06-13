from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def home_page():

    return f'<p> Home page <p>'

@app.route("/<name>")
def home(name):

    return f'<p> Hello {name} <p>'




if __name__ == '__main__':
    app.run()

