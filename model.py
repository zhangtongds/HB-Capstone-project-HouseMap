"""Models and database functions for Properties project."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """User of properties website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    # zipcode = db.Column(db.String(15), nullable=True)

class Favorite(db.Model):
    """properities that users marked as favorite."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    property_id = db.Column(db.Integer, db.ForeignKey('properties.property_id'))

    __tablename__ = "favorites"

class Search(db.Model):
    """User searches for properties"""

    __tablename__ = "searches"

    search_id = db.Column(db.Ingeter, autoincrement=True, primary_key=True)
    address = db.Column(db.String(250), nullable=True)
    zipcode = db.Column(db.Integer, nullable=True)
    no_of_room = db.Column(db.Integer, nullable=False)
    no_of_bath = db.Column(db.Float, nullable=False)


class Property(db.Model):
    """Property information."""

    __tablename__ = "properties"

    property_id = db.Column(db.Integer, primary_key=True)
    zipcode = db.Column(db.Integer, db.ForeignKey('searches.zipcode'))
    proterty_address = db.Column(db.Integer, db.ForeignKey('searches.address'))
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    zillow_url = db.Column(db.String(200), nullable=True) #Needs to envolves in Zillow API


class Sale(db.Model):
    """Sale Details."""

    __tablename__ = "sales"


    sale_id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.property_id'))
    sale_trans_date = db.Column(db.Datetime, nullable=True)
    sale_amount = db.Column(db.Float, nullable=False)
    no_of_room = db.Column(db.Integer, nullable=False)
    no_of_bath = db.Column(db.Float, nullable=False)


# Helper functions
def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///properties'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)

if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."