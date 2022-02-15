import os
import re

from flask import Flask, redirect, render_template, render_template_string, url_for, session, request
from flask_session import Session
from tempfile import mkdtemp
from cs50 import SQL
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import json
import subprocess

from helpers import login_required

# fucntion de crawl photo


app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///databse.db'
Session(app)

db = SQL("sqlite:///database.db")

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        return render_template("login.html")
    else:
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

        # Redirect user to crawl page
        return render_template("crawl.html")

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

@app.route("/logout")
def logout():
    """Log user out"""
    
    #clear the session
    session.clear()

    #redirect the user the index page
    return redirect("/")

@app.route('/crawl', methods=["GET", "POST"])
@login_required
def crawl():
    #TODO: Initiate the crawling fucntion once the user press "GO"
    #TODO: Add (potential) loading screen while the crawler works
    #TODO: Redirect the user once the crawling is finished

    if request.method == "POST":
        # url field empty
        if not request.form.get("url"):
            return render_template("crawl.html", error="Url field is empty")

        # try the function to see if if returns an error
        try:
            crawl_type = request.form["crawl-type"]
        except: # if error then return error msg
            return render_template("crawl.html", error = "Crawl type has not been chosen.")


        # scrapy crawl photos -a start_url="https://unsplash.com/
        if crawl_type == "photo":
            spider_photo = "photos"
            url = request.form.get("url")
            cli_url = "start_url=" + url
            subprocess.check_output(['scrapy', 'crawl', spider_photo, "-a", cli_url], cwd="web_scrapping")
            return render_template("data_photo.html")

        if crawl_type == "text":
            return render_template("data_text.html")
    else:
        return render_template("crawl.html")


@app.route('/data_text')
@login_required
def data_text():

    #TODO: Add data lake upload option
    return render_template("data_text.html")

@app.route('/data_photo', methods=["GET","POST"])
@login_required
def data_photo():
    #TODO: Add data lake upload option

    if request.method == "POST":
        return render_template('data_photo.html')
    else:
        # use os.listdir
        photos = os.listdir('static/local_folder/full')
        return render_template('data_photo.html', photos=photos)

if __name__ == "__main__":
    app.run(debug=True)
