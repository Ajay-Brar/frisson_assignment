from flask import Flask, render_template, request
from backend import call  # Make sure backend.py and app.py are in the same folder
import pandas as pd
from pathlib import Path

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    data = []
    query = ""
    if request.method == 'POST':
        query = request.form['query']
        data = call(query)
    
    return render_template('index.html', data=data, query=query)

if __name__ == '__main__':
    app.run(debug=True)
