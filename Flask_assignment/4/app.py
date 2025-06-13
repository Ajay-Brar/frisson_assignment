from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def home_page():

    return render_template("index.html")

@app.route("/name",methods = ['POST'])
def home():
    Name = request.form['Name']
    
    return f'<p> Hello {Name} <p>'




if __name__ == '__main__':
    app.run()

