import os
from flask import Blueprint, redirect, render_template, request, session

from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash

# creates a blueprint object to organize app components
main = Blueprint("main", __name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///userbase.db")

# when main route is accessed, deliver client to index page
@main.route("/")
def index():
    return render_template("index.html")


@main.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@main.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("login.html", "must provide username", True, 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("login.html", "must provide password", True, 403)

        username = request.form.get("username")
        print(username)
        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", username
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["password"], request.form.get("password")
        ):
            return apology("login.html", "invalid username and/or password", True, 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")


@main.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form

    return redirect("/")


@main.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        existing_names = db.execute(
            "SELECT username FROM users WHERE username = ?",
            request.form.get("username"),

        )
        existing_emails = db.execute(
            "SELECT email FROM users WHERE email = ?",
            request.form.get("email"),
        )

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("register.html", "must provide username", True, 400)
        # check if username already exists
        elif len(existing_names) != 0:
            return apology("register.html", "must provide new username", True, 400)

        # render an apology if password input is blank
        if not request.form.get("password"):
            return apology("register.html", "must provide password", True, 400)
        # render an apology if confirmation input is blank
        if not request.form.get("password"):
            return apology("register.html", "must provide password", True, 403)
        # passwords do not match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("register.html", "confirmation must match password", True, 400)

        # Ensure email was submitted
        if not request.form.get("email"):
            return apology("register.html", "must provide email", True, 400)
        # check if email already exists
        elif len(existing_emails) != 0:
            return apology("register.html", "must provide new email", True, 400)
        email = request.form.get("email")
        # check email is valid
        at_count = 0
        for char in email:
            if char == "@":
                at_count += 1
        # must be one "@"
        if at_count != 1:
            return apology("register.html", "Email must include one '@' and one '.'", True, 400)

        # take community tag and top level domain (tld) from domain of email
        email_parts = email.split("@")
        domain = email_parts[1]
        dot_count = 0
        for char in domain:
            if char == ".":
                dot_count += 1
         # must be one "." in tld
        if dot_count != 1:
            return apology("register.html", "Email must include one '@' and one '.'", True, 400)
        domain_parts = domain.split(".")
        tld = domain_parts[1]

        # ensure email is an edu email
        if tld != "edu":
            return apology("register.html", "Must be school email", True, 400)

        # get community tag from email
        community = domain_parts[0]
        ivy_league = ["brown", "columbia", "cornell", "dartmouth", "harvard", "upenn", "princeton", "yale"]
        if community not in ivy_league:
            return apology("register.html", "Must be Ivy-League school", True, 400)

        # store password, username in python variables
        username = request.form.get("username")
        password = request.form.get("password")
        # store hash version of password
        hash = generate_password_hash(password, method="pbkdf2", salt_length=16)
        db.execute("INSERT INTO users (username, password, community, email) VALUES (?, ?, ?, ?)", username, hash, community, email)

        # log the user in
        return login()

    return render_template("register.html")


@main.route("/scores", methods=["GET", "POST"])
def scores():
    """Get users Big Five Personality Test scores"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        session["user_id"] = session.get("user_id")
        ocean = "ocean"

        # for each big five personality trait
        for trait in ocean:
            # Ensure username was submitted
            if not request.form.get(trait):
                return apology("scores.html", "Must provide score for each trait", True, 400)
            # try to get scores from user
            try:
                score = int(request.form.get(trait))
            except:
                return apology("scores.html", "Not an integer", True, 400)
            # if scores are not between 0-100
            if (score < 0) or (score > 100):
                return apology("scores.html", "Scores must be between 0 and 100", True, 400)

        # check if scores have already been inputted
        existing_ids = db.execute(
            "SELECT user_id FROM scores WHERE user_id = ?",
            session["user_id"])

        # if scores exists
        if len(existing_ids) != 0:
            return apology("scores.html", "scores already exist", True, 400)

        # set values for scores
        o = int(request.form.get("o"))
        c = int(request.form.get("c"))
        e = int(request.form.get("e"))
        a = int(request.form.get("a"))
        n = int(request.form.get("n"))

        # update database
        db.execute("INSERT INTO scores (user_id, openness, conscientiousness, extraversion, agreeableness, neuroticism) VALUES (?, ?, ?, ?, ?, ?)", session["user_id"], o, c, e, a, n)
        return queue()

    print(session["user_id"])
    return render_template("scores.html")


@main.route("/queue")
def queue():
    """OPEN QUEUE PAGE"""
    session["user_id"]

    # check if scores exist for user
    scores_exist = db.execute("SELECT * FROM scores WHERE user_id = ?", session["user_id"])
    # if they exist, render queue
    if scores_exist:
        return render_template("queue.html")
    # send user back to scores
    else:
        return redirect("/scores")

# apology function to handle user errors
def apology(html, message, error, code=400):
    """Render message as an apology to user."""
    return render_template(html, message=message, error=error, code=code)
