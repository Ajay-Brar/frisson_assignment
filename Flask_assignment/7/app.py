from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)

# Create tables
with app.app_context():
    db.create_all()

# Home / Read
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

# Create
@app.route('/add', methods=['POST'])
def add_user():
    name = request.form['name']
    email = request.form['email']
    new_user = User(name=name, email=email)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('index'))

# Update
@app.route('/update/<int:id>', methods=['POST'])
def update_user(id):
    user = User.query.get_or_404(id)
    name = request.form['name']
    email = request.form['email']

    print(f"[UPDATE] User ID: {id}, New Name: {name}, New Email: {email}")

    user.name = name
    user.email = email

    try:
        db.session.commit()
        print("[UPDATE] Commit successful")
    except Exception as e:
        db.session.rollback()
        print("[UPDATE] Failed to commit:", e)

    return redirect(url_for('index'))


# Delete
@app.route('/delete/<int:id>')
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
