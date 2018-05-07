import os

import httplib
from flask import Flask, render_template, request, flash, redirect
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.secret_key = "ABC"
ONBOARD_KEY=os.environ['ONBOARD_KEY']

print ONBOARD_KEY
# ONBOARD_URL = ""

conn = httplib.HTTPSConnection("search.onboard-apis.com") 

headers = { 
    'accept': "application/json", 
    'apikey': ONBOARD_KEY, 
    } 

conn.request("GET", "/propertyapi/v1.0.0/property/detail?address1=4529%20Winona%20Court&address2=Denver%2C%20CO", headers=headers) 

res = conn.getresponse() 
data = res.read() 

print(data.decode("utf-8"))