"""Models and database functions for Properties project."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """User of properties website."""

    __tablename__ = "users"

    fname = db.Column(db.String(25), nullable=False)
    lname = db.Column(db.String(25), nullable=False)
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64))
    password = db.Column(db.String(64))
    zipcode = db.Column(db.String(15))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User fname={} lname={} zipcode= {} user_id={} email={}>".format(self.fname, self.lname, self.zipcode, self.user_id, self.email)

# class Favorite(db.Model):
#     """properities that users marked as favorite."""

#     __tablename__ = "favorites"

#     favorite_id = db.Column(db.Integer, autoincrement=True,  primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
#     property_id = db.Column(db.String(250), db.ForeignKey('properties.property_id'))

#     def __repr__(self):
#         """Provide helpful representation when printed."""

#         return "<Favorite favorite_id={} user_id={} property_id={}>".format(self.favorite_id, self.user_id, self.property_id)

#     user = db.relationship("User", backref=db.backref("favorites", order_by=favorite_id))

#     _property = db.relationship("Property", backref=db.backref("favorites", order_by=favorite_id))

class Search(db.Model):
    """User searches for properties"""

    __tablename__ = "searches"

    search_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    address = db.Column(db.String(250))
    zipcode = db.Column(db.Integer)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    trans_type = db.Column(db.String(10))
    max_no_bed = db.Column(db.Integer)
    min_no_bed = db.Column(db.Integer)
    max_no_bath = db.Column(db.Integer)
    min_no_bath = db.Column(db.Integer)
    price_from = db.Column(db.Integer)
    price_to = db.Column(db.Integer)
    trans_date_from = db.Column(db.DateTime)
    trans_date_to = db.Column(db.DateTime)
    property_type = db.Column(db.String(50))
    saved_by_user = db.Column(db.Boolean)
    saved_date = db.Column(db.DateTime)

    user = db.relationship("User", backref=db.backref("searches", order_by=search_id))




    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Search search_id={} user_id={} address={} zipcode={} city={} state={} trans_type={} max_no_bed={} min_no_bed={} max_no_bath={} min_no_bath={} price_from={} price_to={} trans_date_from={} trans_date_to={} property_type={} saved_by_user={} saved_date={}>".format(self.search_id, self.user_id, self.address, self.zipcode, self.city, self.state, self.trans_type, self.max_no_bed, self.min_no_bed, self.max_no_bath, self.min_no_bath, self.price_from, self.price_to, self.trans_date_from, self.trans_date_to, self.property_type, self.saved_by_user, self.saved_date)


class Property(db.Model):
    """Property information."""

    __tablename__ = "properties"

    property_id = db.Column(db.String(250), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    address = db.Column(db.String(250))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    zillow_url = db.Column(db.String(200)) #Needs to involve in Zillow API
    no_of_beds = db.Column(db.Integer)
    no_of_baths = db.Column(db.Float)
    saved_date = db.Column(db.DateTime)
    saved_by_user = db.Column(db.Boolean)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Property property_id={} self.user_id={} address={} latitude={} longitude={} zillow_url={} no_of_beds={} no_of_baths={} >".format(self.property_id, self.user_id, self.address, self.latitude, self.longitude, self.no_of_beds, self.no_of_baths)

class Sale(db.Model):
    """Sale Details."""

    __tablename__ = "sales"


    sale_id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.String(250), db.ForeignKey('properties.property_id'))
    sale_trans_date = db.Column(db.DateTime)
    sale_amount = db.Column(db.Float, nullable=False)

    _property = db.relationship("Property", backref=db.backref("sales", order_by=sale_id)) 

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Sale sale_id={} property_id={} sale_trans_date={} sale_amount={}>".format(self.sale_id, self.property_id, self.sale_trans_date, self.sale_amount)


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