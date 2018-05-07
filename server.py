from pprint import pformat
import os

import requests
import httplib
from flask import Flask, render_template, request, flash, redirect
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.secret_key = "ABC"
ONBOARD_KEY=os.environ['ONBOARD_KEY']

# ONBOARD_URL = ""

# conn = httplib.HTTPSConnection("search.onboard-apis.com") 

# headers = { 
#     'accept': "application/json", 
#     'apikey': ONBOARD_KEY, 
#     } 

# conn.request("GET", "/propertyapi/v1.0.0/property/detail?address1=4529%20Winona%20Court&address2=Denver%2C%20CO", headers=headers) 

# res = conn.getresponse() 
# data = res.read() 

# print(data.decode("utf-8"))

@app.route("/")
def homepage():
    """Show homepage."""

    return render_template("homepage.html")


if __name__ == "__main__":
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(app)
    app.run(host = '0.0.0.0')