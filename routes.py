from flask import Blueprint, render_template, session, redirect, request, current_app, url_for, abort, flash
from movie_library.forms import MovieForm, ExtendedMovieForm, RegisterForm, Loginform
from movie_library.models import Movie, User
from dataclasses import asdict
import uuid
import datetime
from passlib.hash import pbkdf2_sha256
import functools


pages = Blueprint("pages", __name__, template_folder="tempaltes", static_folder="static")


# Decorater for protected endpoints
def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get("email") is None:
            return redirect(url_for(".login"))
        
        return route(*args, **kwargs)
    return route_wrapper



@pages.route("/")
@login_required
def index():
    user_data = current_app.db.user.find_one({"email": session["email"]})
    user = User(**user_data)


    movie_data = current_app.db.movie.find({"_id": {"$in": user.movies}}) # find all movies inn our db
    movies = [Movie(**movie) for movie in movie_data] # iterate all movies and pass each one as unpacked args
    
    return render_template("index.html", title="Movies Watchlist", movies_data=movies)




@pages.route("/register", methods=["GET", "POST"])
def register():
    if session.get("email"): # if the user is already logged in
        return redirect(url_for(".index"))
    
    form = RegisterForm() # if the user is not logged in

    if form.validate_on_submit():
        # create the user
        user = User(
            _id = uuid.uuid4().hex,
            email=form.email.data,
            password=pbkdf2_sha256.hash(form.password.data)
        )

        current_app.db.user.insert_one(asdict(user))
        flash("User successfully registered", "success")
        
        return redirect(url_for(".login"))

    return render_template("register.html", title="Movies Watchlist = Register", form=form)    




@pages.route("/login", methods=["GET", "POST"])
def login():
    if session.get("email"): # if user is logged in
        return redirect(url_for(".index"))
    
    form = Loginform()

    if form.validate_on_submit():
        user_data = current_app.db.user.find_one({"email": form.email.data})
        if not user_data:
            flash("Login credentials are not correct.", category="danger")
            return redirect(url_for(".login"))
        
        user = User(**user_data)
        if user and pbkdf2_sha256.verify(form.password.data, user.password):
            # populating the session
            session["user_id"] = user._id
            session["email"] = user.email

            return redirect(url_for(".index"))
        
        # if something went wrong
        flash("Login credentials are not correct.", category="danger")

    return render_template("login.html", title="Movie Watchlist - Login", form=form)


@pages.route("/logout")
def logout():
    # logout but keep the same themes
    keep_theme = session.get("theme")
    session.clear()
    session["theme"] = keep_theme

    return redirect(url_for(".login"))





@pages.get("/movie/<string:_id>")
def movie(_id):
    movie_data = current_app.db.movie.find_one({"_id": _id})
    if not movie_data:
        abort(404)
    movie = Movie(**movie_data) # unpack dictionary
    
    return render_template("movie_details.html", movie=movie)




@pages.route("/add", methods=["GET", "POST"])
@login_required
def add_movie():
    # Create form object
    form = MovieForm()

    # Checks if form has been submitted
    # Cheks the validation as well
    # Populates the database
    if form.validate_on_submit():
        movie = Movie(
            _id = uuid.uuid4().hex,
            title = form.title.data,
            director = form.director.data,
            year = form.year.data
        )
        
        current_app.db.movie.insert_one(asdict(movie))
        current_app.db.user.update_one({"_id": session["user_id"]}, {"$push": {"movies": movie._id}})


        #return redirect(url_for(".index"))
        return redirect(url_for(".movie", _id=movie._id))

    return render_template("new_movie.html", title="Movies Watchlist - Add Movie", form=form)



# Update the Movie obj to ExtentedMovie obj
@pages.route("/edit/<string:_id>", methods=["GET", "POST"])
@login_required
def edit_movie(_id):
    movie = Movie(**current_app.db.movie.find_one({"_id": _id}))
    form = ExtendedMovieForm(obj=movie)

    if form.validate_on_submit():
        movie.title = form.title.data
        movie.director = form.director.data
        movie.year = form.year.data
        movie.cast = form.cast.data
        movie.series = form.series.data
        movie.tags = form.tags.data
        movie.description = form.description.data
        movie.video_link = form.video_link.data

        current_app.db.movie.update_one({"_id": movie._id}, {"$set": asdict(movie)})
        return redirect(url_for(".movie", _id=movie._id))
    
    return render_template("movie_form.html", movie=movie, form=form)


@pages.get("/movie/<string:_id>/rate")
@login_required
def rate_movie(_id):
    rating = int(request.args.get("rating"))
    current_app.db.movie.update_one({"_id": _id}, {"$set": {"rating": rating}})

    return redirect(url_for(".movie", _id=_id))



@pages.get("/movie/<string:_id>/watch")
@login_required
def watch_today(_id):
    current_app.db.movie.update_one({"_id": _id}, {"$set": {"last_watched": datetime.datetime.today()}})

    return redirect(url_for(".movie", _id=_id))



@pages.get("/toggle-theme")
def toggle_theme():
    # current_theme will be none the first time, so default will be a light theme
    current_theme = session.get("theme")
    if current_theme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark"

    # When we switch themes, we dont want to redirect to another page
    # We want to stay on the current page we are at
    return redirect(request.args.get("current_page"))


