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


@app.route("/user-page/<user_id>")
def user_page(user_id):
    """Show user details."""

    user = User.query.filter(User.user_id == user_id).first()
    print user

    age = user.age
    zipcode = user.zipcode

    user_ratings = user.ratings

    return render_template("user-page.html",
                           user_id=user_id,
                           age=age,
                           zipcode=zipcode,
                           ratings=user_ratings)


@app.route("/movies")
def movie_list():
    """Show list of movies"""

    movies = Movie.query.order_by("title").all()

    return render_template("movie_list.html", movies=movies)


@app.route("/movie-page/<movie_id>")
def movie_page(movie_id):
    """Show movie details."""

    if 'user_id' in session:
        user_id = session['user_id']
    else:
        user_id = None

    movie = Movie.query.filter(Movie.movie_id == movie_id).first()
    user_rating = Rating.query.filter(Rating.user_id == user_id,
                                      Rating.movie_id == movie_id).first()
    if movie:

        m_ratings = movie.ratings

        return render_template("movie-info.html",
                               movie=movie,
                               ratings=m_ratings,
                               user_rating=user_rating)
    else:
        flash("There's nothing there. Pick a movie.")
        return redirect("/movies")


@app.route("/process-rating", methods=["POST"])
def process_rating():

    movie_id = request.form.get("movie_id")
    print movie_id
    new_score = request.form.get("new_rating")
    user_id = session['user_id']

    user_rating = Rating.query.filter(Rating.user_id == user_id,
                                      Rating.movie_id == movie_id).first()

    if user_rating:
        #update rating
        user_rating.score = new_score
        flash('Your rating was successfully updated.')
    else:
    #add new rating
        # show('new_rating')
        # hide('update_rating')
        new_rating = Rating(movie_id=movie_id,
                            user_id=user_id,
                            score=new_score,)

        db.session.add(new_rating)
        flash('Your rating was successfully added.')

    db.session.commit()
    url = "/movie-page/" + str(movie_id)
    return redirect(url)


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
        url = "/user-page/" + str(user.user_id)
        return redirect(url)
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
