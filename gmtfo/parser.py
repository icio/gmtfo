import re
import sys
from random import sample

from gmtfo.db import connect_to_database
from gmtfo.db import get_random_airports


places = re.compile(r"""\W(?=to|from|via)""", flags=re.IGNORECASE)
time = re.compile(r"""
\b(
    (jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)|
    (days?|weeks?|months?)\b
)
""", flags=re.IGNORECASE | re.VERBOSE)
reverse_time_sep = re.compile(r"""
\b(ni|trefa|nihtiw|reofeb)\b
""", flags=re.IGNORECASE | re.VERBOSE)


def parse(db, phrase):
    """
    CAUTION: SRS DATA MUNGING
    """

    if phrase:
        phrase = phrase.strip()
    if not phrase:
        return {
            "random": True,
            "routes": random_routes(db)
        }

    # Separate the places from the time
    phrase_places, phrase_times = None, None
    time_unit_start = time.search(phrase)
    if time_unit_start:
        time_sep = reverse_time_sep.search(phrase[::-1])
        if time_sep:
            time_sep = len(phrase)-time_sep.end()
            phrase_places = phrase[:time_sep].strip()
            phrase_times = phrase[time_sep:].strip()

    if phrase_places is None:
        phrase_places = phrase
        phrase_times = ""

    # Determine the order of the places
    scopes = [None, 'from', 'via', 'to']
    required_scopes = ['from', 'to']
    phrase_places = places.split(phrase_places)
    for i, place in enumerate(phrase_places):
        place, scope = place.split(' '), None
        if len(place) > 1 and place[0] in scopes:
            if place[0] in required_scopes:
                required_scopes.remove(place[0])
            scope, place = place[0], place[1:]
        phrase_places[i] = {'query': " ".join(place), 'scope': scope}
    phrase_places = sorted(
        phrase_places, key=lambda p: p['scope'],
        cmp=lambda a, b: scopes.index(a) - scopes.index(b)
    )
    if phrase_places[0]['scope'] is None:
        for place in phrase_places:
            if place['scope'] is None:
                place['scope'] = required_scopes.pop(0) if required_scopes \
                    else 'to'
            else:
                break
        phrase_places = sorted(
            phrase_places, key=lambda p: p['scope'],
            cmp=lambda a, b: scopes.index(a) - scopes.index(b)
        )

    return {
        'checkpoints': phrase_places,
        'times': phrase_times
    }


def random_routes(db):
    airports = get_random_airports(db)
    destinations = sample(airports, len(airports)/2)
    origins = [a for a in airports if a not in destinations]
    return zip(destinations, origins)


if __name__ == "__main__":

    from pprint import pprint

    queries = (
        "from london to melbourne in november",
        "melbourne from london within 7 days' time",
        "london to melbourne via bangkok in a few days",
        "via sao paulo from berlin to munich",
    )
    for q in queries:
        print "%s -> " % q
        pprint(parse(connect_to_database(), q))
