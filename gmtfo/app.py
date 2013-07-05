from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
app = Flask(__name__)

from db import get_db as db_conn
from db import close_connection
app.teardown_appcontext(close_connection)

from db import get_city_airports


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/routes")
def routes():

    db = db_conn()
    from random import choice
    london = choice(get_city_airports(db, "london"))
    melbourne = choice(get_city_airports(db, "melbourne"))

    return jsonify(
        query=request.args.get('query'),
        routes=((london, melbourne),),
        dates=('2013-01-01', '2013-01-02', '2013-01-03')
    )
