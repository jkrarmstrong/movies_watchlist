import os
from flask import Flask
from dotenv import load_dotenv
from pymongo import MongoClient

from movie_library.routes import pages

load_dotenv() # load the .env file

def create_app():
    app = Flask(__name__)
    
    # Populate MONGODB_URI and secret key
    app.config["MONGODB_URI"] = os.environ.get("MONGODB_URI")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "secret_key_should_be_here")

    # Set database to MoncoClient default database
    app.db = MongoClient(app.config["MONGODB_URI"]).get_default_database()

    # Register the blueprint from pages
    app.register_blueprint(pages)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=False)