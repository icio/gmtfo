from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
app = Flask(__name__)

from gmtfo.db import get_db
from gmtfo.db import close_connection
app.teardown_appcontext(close_connection)

from gmtfo.parser import parse


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/routes")
def routes():

    query = request.args.get('query') or ''
    resp = parse(get_db(), query)
    resp.setdefault('routes', [])

    return jsonify(
        query=query,
        **resp
    )
