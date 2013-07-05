from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
app = Flask(__name__)

from db import get_db as db_conn
from db import close_connection
app.teardown_appcontext(close_connection)

from random import sample
from db import get_city_airports


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/routes")
def routes():

    query = request.args.get('query')
    routes, dates = [], ('2013-01-01', '2013-01-02', '2013-01-03')

    query = query.split(' to ', 1)
    if len(query) == 2:
        try:
            db, limit = db_conn(), 5
            origin = sample(get_city_airports(db, query[0]), limit)
            destin = sample(get_city_airports(db, query[1]), limit)
            for o, d in zip(origin, destin):
                routes.append((o, d))
        except:
            pass

    return jsonify(
        query=query,
        routes=routes,
        dates=dates
    )
