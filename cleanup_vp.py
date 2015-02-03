
import json


def get_corr():
    with open('cleanups.json', 'r') as input:
        return json.loads(input.read())
    return None


def get_beers():
    with open('beers.json', 'r') as input:
        return json.loads(input.read())


cleanups = get_corr()


def cleanup(name):
    if name in cleanups:
        return cleanups[name]
    return name


beers = get_beers()

for beer in beers:
    beer['brewery'] = cleanup(beer['brewery'])

with open('beers_cleaned.json', 'w') as out:
    out.write(json.dumps(beers))
