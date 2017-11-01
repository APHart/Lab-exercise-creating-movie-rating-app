"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, jsonify, render_template, redirect,
                   request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import (connect_to_db, db, User, Rating, Movie)


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    # a = jsonify([1,3])
    # return a
    # session['user_id'] = None tried this but not correct

    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/register", methods=["GET"])
def register_form():
    """Shows user registration form."""

    return render_template("register_form.html")


@app.route("/register", methods=["POST"])
def register_process():
    """Adds new user and redirects to homepage."""
    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter(User.email == email).first()

    # print users[0]
    if user:
        flash('That email address is already registered, please go to log in.')
        return redirect("/login")
    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    flash('Successfully registered.')
    return redirect("/")


@app.route("/login", methods=["GET"])
def login():
    """User account login."""
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_process():
    """User account login process."""

    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter(User.email == email).first()
    if not user:
        flash('This email is not registered, please register.')
        return redirect("/register")

    if user.password == password:
        session['user_id'] = user.user_id
        flash('You have successfully logged in...woohoo!')
        return redirect("/")
    else:
        flash('Incorrect password, please try again')
        return redirect("/login")


@app.route("/logout", methods=["POST"])
def logout():
    """User account logout."""
    # session.pop removes user_id key/value from session, does not set value to none
    # session.pop('user_id', None)
    # print session['user_id']

    #delete user_id from session
    del session['user_id']
    flash('You have successfully logged out...bye!')

    return redirect("/")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)


    app.run(port=5000, host='0.0.0.0')
