import nltk
from random import sample

from gmtfo.db import get_random_airports


def random_routes(db):
    airports = get_random_airports(db)
    destinations = sample(airports, len(airports)/2)
    origins = [a for a in airports if a not in destinations]
    return zip(destinations, origins)


def parse(db, query):
    if query:
        query = query.strip()
    if not query:
        return {
            "random": True,
            "routes": random_routes(db)
        }

    query = query.replace('.', ' ')
    query = nltk.word_tokenize(query)
    query = nltk.pos_tag(query)
    
    return {
        'parsed_query': query
    }
