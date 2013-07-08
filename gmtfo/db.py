import sqlite3
import csv
import os.path

from flask import g
from whoosh.index import create_in, open_dir
from whoosh.qparser import MultifieldParser
from whoosh.fields import *

DATABASE = os.path.dirname(__file__)+'/../airports.db'
ROUTE_SOURCE = os.path.dirname(__file__)+'/../routes.csv'
AIRPORT_SOURCE = os.path.dirname(__file__)+'/../airports.csv'
INDEX_DIR = os.path.dirname(__file__)+'/../airports.index'

if __name__ != "__main__":
    ix = open_dir(INDEX_DIR)
    mparser = MultifieldParser(["code", "name"], ix.schema)
    searcher = ix.searcher()


def find_places(term, limit=5):
    return searcher.search(mparser.parse(term), limit=limit)


def get_city_airports(db, city_id):
    c = db.cursor()
    c.execute("SELECT * FROM airport WHERE city_id = ? AND "
              "iata_faa IS NOT NULL ORDER BY country", (city_id,))
    return c.fetchall()


def get_cities(db, city):
    city = "%%%s%%" % city.replace(' ', '%')
    c = db.cursor()
    c.execute("SELECT rowid, fullname FROM city WHERE fullname LIKE ? LIMIT 3",
              (city,))
    return c.fetchall()


def get_random_airports(db, limit=10):
    c = db.cursor()
    c.execute("SELECT * FROM airport ORDER BY RANDOM() LIMIT %d" % limit)
    return c.fetchall()


def connect_to_database():
    db = sqlite3.connect(DATABASE)
    db.row_factory = dict_factory
    return db


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def load_db(db):
    c = db.cursor()

    print "Loading data into memory"  # because lulz

    # Cities
    c.execute("SELECT rowid as id, fullname as name FROM city")
    cities = {}
    for city in c.fetchall():
        city['airports'] = []
        cities[city['id']] = city

    # Airports
    c.execute("SELECT id, name, iata_faa as code, city_id, city, country, lat,"
              "lon FROM airport WHERE iata_faa IS NOT NULL")
    airports = {}
    for airport in c.fetchall():
        airport['next'] = []
        cities[airport['city_id']]['airports'].append(airport)
        airports[airport['id']] = airport

    # Routes
    c.execute("SELECT DISTINCT source_airport_id, dest_airport_id "
              "FROM route WHERE source_airport_id IS NOT NULL AND "
              "dest_airport_id IS NOT NULL")
    for route in c.fetchall():
        dest = route['dest_airport'] = airports[route['dest_airport_id']]
        src = route['source_airport'] = airports[route['source_airport_id']]
        if dest not in src.get('next', []):
            print dest['code'], '->', src['code'], '#next'
            route['source_airport']['next'].append(route['dest_airport'])
        if src not in dest.get('next', []):
            print src['code'], '->', dest['code'], '#next'
            route['dest_airport']['next'].append(route['source_airport'])

    print "Loaded"

    return cities, airports


def build_index(index_dir):
    """
    Create a whoose full-text index of the named entities
    """
    if not os.path.isdir(index_dir):
        os.mkdir(index_dir)

    # Prepare the whoosh index for population
    schema = Schema(code=TEXT(stored=True), name=TEXT(stored=True),
                    type=STORED, id=STORED)
    ix = create_in(index_dir, schema)
    writer = ix.writer()

    # Populate the whoosh name index
    cities, airports = load_db(connect_to_database())
    for city in cities.itervalues():
        writer.add_document(type=1, id=city['id'], name=city['name'])
    for airport in airports.itervalues():
        name = "%s, %s, %s" % (airport['name'], airport['city'],
                               airport['country'])
        writer.add_document(type=0, id=airport['id'], name=name,
                            code=airport['code'])
    writer.commit()


def build_db(airport_source, route_source):
    """
    Create a SQLite database of the CSV data that we collected from openflights
    """
    db = connect_to_database()
    c = db.cursor()

    # Build the airport table
    c.execute("DROP TABLE IF EXISTS airport;")
    c.execute("CREATE TABLE airport (id INT, name TEXT, city TEXT, city_id INT"
              ", country TEXT, iata_faa TEXT, icao TEXT, lat REAL, lon REAL, "
              "alt REAL, timezone TEXT, dst TEXT);")

    # Populate the database table
    print "reading %s" % airport_source
    with open(airport_source, 'rb') as source:
        reader = csv.reader(source)
        for row in reader:
            row = map(lambda s: unicode(s, "utf8"), row)
            c.execute("INSERT INTO airport (id, name, city, city_id, country, "
                      "iata_faa, icao, lat, lon, alt, timezone, dst) VALUES "
                      "(?, ?, ?, NULL, ?, ?, ?, ?, ?, ?, ?, ?)", row)

    # Null certain columns
    c.execute("UPDATE airport SET iata_faa=NULL "
              "WHERE iata_faa IN ('\\N', '')")
    c.execute("UPDATE airport SET icao = NULL WHERE icao IN ('\\N', '')")

    # Build the cities table
    c.execute("DROP TABLE IF EXISTS city;")
    c.execute("CREATE TABLE city (id INT PRIMARY KEY, fullname TEXT, name TEXT"
              ", country TEXT)")
    c.execute("INSERT INTO city (name, country, fullname) SELECT airport.city,"
              "country, airport.city || ', ' || country AS fullname FROM "
              "airport GROUP BY country, airport.city")
    c.execute("UPDATE airport SET city_id = (SELECT rowid FROM city WHERE "
              "city.name=airport.city AND city.country=airport.country)")

    # Build the routes table
    c.execute("DROP TABLE IF EXISTS route;")
    c.execute("CREATE TABLE route (airline TEXT, airline_id INT, "
              "source_airport TEXT, source_airport_id INT, dest_airport TEXT, "
              "dest_airport_id INT, codeshare TEXT, stops INT, equip TEXT)")

    # Populate the route table
    print "reading %s" % route_source
    with open(route_source, 'rb') as source:
        reader = csv.reader(source)
        for row in reader:
            row = map(lambda s: unicode(s, "utf8"), row)
            c.execute("INSERT INTO route (airline, airline_id, source_airport,"
                      " source_airport_id, dest_airport, dest_airport_id, "
                      "codeshare, stops, equip) VALUES (?, ?, ?, ?, ?, ?, ?, "
                      "?, ?)", row)
    c.execute("UPDATE route SET dest_airport_id=NULL "
              "WHERE dest_airport_id='\N'")
    c.execute("UPDATE route SET source_airport_id=NULL "
              "WHERE source_airport_id='\N'")

    # The database has now been populated. It is interactively browsable using
    # `sqlite airports.db`

    db.commit()
    db.close()


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db


def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == "__main__":
    build_db(AIRPORT_SOURCE, ROUTE_SOURCE)
    build_index(INDEX_DIR)
    # from pprint import pprint
    # pprint(get_city_airports(connect_to_database(), "london"))
