import os
import re

from flask import Flask, redirect, render_template, url_for, session, request
from flask_session import Session
from tempfile import mkdtemp
from cs50 import SQL
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# fucntion de crawl photo


app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///databse.db'
db = SQLAlchemy(app)
Session(app)

db = SQL("sqlite:///database.db")

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", error_msg="Username field is empty")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", error_msg="Password field is empty")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html", error_msg="Invalid Username or Password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return render_template('data.html')

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Register user"""
    if request.method == "POST":

        # Getting data from the user's register form
        username = request.form.get("username")
        password = request.form.get("password")
        retypepw = request.form.get("retypepw")
        username_database = db.execute("SELECT username FROM users WHERE username=?", username)

        # Check if the data is empty
        if not username:
            return render_template("signup.html", error_msg="Missing username")
        
        elif not password:
            return render_template("signup.html", error_msg="Missing password")
        
        elif not retypepw:
            return render_template("signup.html", error_msg="Missing confimation password")

        # Check if username is taken
        if len(username_database) > 0:
            if username == username_database[0]["username"]:
                return render_template("signup.html", error_msg="Username has been taken!")

        # Check if pw and retype are the same
        if password != retypepw:
            return render_template("signup.html", error_msg="Your password and confirmation password does not match!")

        # Check if username has already been used
        if username in db.execute("SELECT username FROM users;"):
            return render_template("signup.html", error_msg="The username has already been used.")
        
        # Hasing the password
        hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        # Insert into the database user info and hashed password
        db.execute("INSERT INTO users (username, hash) VALUES (?,?);", username, hash)
        
        # Redirect user to the index page for them to manually login
        return redirect("/")

    else:
        return render_template("signup.html")

@app.route('/data')
@login_required
def data():
    return render_template("data.html")

@app.route('/data_photo')
@login_required
def data_photo():
    photos = os.listdir(os.path.join(app.static_folder, "test_photo"))
    return render_template('data_photo.html', photos=photos)
if __name__ == "__main__":
    app.run(debug=True)
