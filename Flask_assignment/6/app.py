from flask import Flask, request, render_template, redirect
import pandas as pd

app = Flask(__name__)

file_status = {}  

@app.route("/", methods=['GET'])
def redir():
    return redirect('/upload')

@app.route("/upload", methods=['GET'])
def home_page():
    return render_template('index.html')

@app.route("/result", methods=['POST'])
def res():
    files = request.files.getlist('myfile') 

    for file in files:
        if file and file.filename != "":
            file_status[file.filename] = "Uploaded"

    # Create a DataFrame and return it as an HTML table
    df = pd.DataFrame(file_status.items(), columns=["Filename", "Status"])
    return df.to_html(classes="table", border=1)

if __name__ == '__main__':
    app.run(debug=True)
