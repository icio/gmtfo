from itertools import chain, permutations

from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
app = Flask(__name__)

from gmtfo.db import get_db
from gmtfo.db import close_connection
app.teardown_appcontext(close_connection)

from gmtfo.parser import parse
from gmtfo.db import connect_to_database, find_places, load_db

cities, airports = load_db(connect_to_database())


@app.route("/")
def home():
    return render_template("index.html")


def compute_routes(stages, steps=1):
    complete = [a for aset in stages for a in aset]
    for s in xrange(0, len(stages)-1):
        srcs, dests = stages[s], stages[s+1]

        print "\nstep %d" % s

        step = 0
        queue = [[src] for src in srcs]
        while step < steps and queue:
            step += 1
            next_queue = []
            for path in queue:
                print "%d :" % step, [(a['name'], a['id']) for a in path]
                print len(path[-1].get('next', []))
                for next in path[-1].get('next', []):
                    print "\t%s" % next['name']
                    if next in dests:
                        yield path+[next]
                    elif next not in path and next not in complete:
                        next_queue.append(path + [next])
            queue = next_queue
            print "Next queue:", [a['name'] for route in queue for a in route]


@app.route("/routes")
def routes():

    q = unicode(request.args.get('query') or '')
    query = parse(get_db(), q)

    stages = []
    for checkpoint in query.get('checkpoints'):
        places = list(find_places(checkpoint.get('query')))
        place = checkpoint['place'] = dict(places.pop(0))
        checkpoint['alternatives'] = [dict(d) for d in places]

        if place['type'] == 0:    # Airports
            stages.append([airports[place['id']]])
        elif place['type'] == 1:  # Cities
            stages.append(cities[place['id']]['airports'])

    routes = []
    for route in compute_routes(stages):
        r = []
        for a in route:
            print type(a), dir(a)
            a = a.copy()
            del a['next']
            r.append(a)
        routes.append(r)

    print routes

    resp = {
        'query': q,
        # 'parsed_query': query,
        'checkpoints': query.get('checkpoints')
    }

    return jsonify(**resp)
