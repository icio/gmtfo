import sqlite3
import csv
import os.path
from flask import g


DATABASE = os.path.dirname(__file__)+'/../airports.db'
DATABASE_SOURCE = os.path.dirname(__file__)+'/../airports.csv'


def get_city_airports(db, city):
    city = "%%%s%%" % city.replace(' ', '%')
    c = db.cursor()
    c.execute("SELECT * FROM airport WHERE city LIKE ? AND "
              "iata_faa IS NOT NULL ORDER BY country", (city,))
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


def build_db(database, database_source):
    print "%s opened" % database
    db = connect_to_database()
    c = db.cursor()

    # Build the database table
    c.execute("DROP TABLE IF EXISTS airport;")
    c.execute("CREATE TABLE airport (id INT, name TEXT, city TEXT, "
              "country TEXT, iata_faa TEXT, icao TEXT, lat REAL, lon REAL, "
              "alt REAL, timezone TEXT, dst TEXT);")

    # Populate the database table
    print "reading %s" % database_source
    count = 0
    with open(database_source, 'rb') as source:
        reader = csv.reader(source)
        for row in reader:
            count += 1
            row = map(lambda s: unicode(s, "utf8"), row)
            c.execute("INSERT INTO airport (id, name, city, country, "
                      "iata_faa, icao, lat, lon, alt, timezone, dst) VALUES "
                      "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", row)

    # Null certain columns
    c.execute("UPDATE airport SET iata_faa=NULL "
              "WHERE iata_faa IN ('\\N', '')")
    c.execute("UPDATE airport SET icao = NULL WHERE icao IN ('\\N', '')")

    print "%d rows inserted" % count
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
    # build_db(DATABASE, DATABASE_SOURCE)
    from pprint import pprint
    pprint(get_city_airports(connect_to_database(), "london"))
