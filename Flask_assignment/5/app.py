from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def home_page():
    return render_template('index.html')

@app.route("/info", methods = ['POST'])
def session():
    Name = request.form['Name']
    Age = request.form['Age']
    City = request.form['City']

    return f'''<h1>{Name} Data</h1>
Name = {Name} <br><br>
Age = {Age}<br><br>
City = {City}<br><br>
<a href='/'> Back to Home </a>
'''

if __name__ == '__main__':
    app.run()

