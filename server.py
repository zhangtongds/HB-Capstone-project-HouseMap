import pprint
import os
from jinja2 import StrictUndefined
import requests
# import httplib
from flask import (Flask, render_template, redirect, request, flash,
                   session, jsonify)
from flask_debugtoolbar import DebugToolbarExtension
from model import User, Favorite, Search, Property, Sale, connect_to_db, db
from seed import parse_address_from_homepage
import json

app = Flask(__name__)
app.secret_key = "ABC"
ONBOARD_KEY=os.environ['ONBOARD_KEY']

ONBOARD_URL = "http://search.onboard-apis.com"

# conn = httplib.HTTPSConnection("search.onboard-apis.com") 

headers = { 
    'accept': "application/json", 
    'apikey': ONBOARD_KEY, 
    } 


@app.route("/")
def homepage():
    """Show homepage."""

    return render_template("homepage.html")

@app.route("/search")
def get_user_input():
    """Get user input information."""
    info_type = request.args.get("info_type")
    
    if info_type == 'address':
        address = request.args.get("address")
        city = request.args.get("city")
        state = request.args.get("state")
        # print address, city, state
        address1 = address.replace(" ", "%20")
        address2 = city + "%2C%20" + state
        print address1, address2
        reaquest_url = "/propertyapi/v1.0.0/property/detail?address1=" + address1 + "&address2=" + address2
        print reaquest_url
        response = requests.get(ONBOARD_URL + reaquest_url, headers=headers) 

        data = response.json()
        # json_string = json.dumps(data)
        # data = json.loads(json_string)
        print pprint.pprint(data)
        print data['property'][0]['identifier']['obPropId']
        
    return render_template("search-results.html")



if __name__ == "__main__":
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(app)
    app.run(host = '0.0.0.0')