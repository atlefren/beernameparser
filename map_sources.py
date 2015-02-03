# -*- coding: utf-8 -*-

import re

from database import init_db
from models import (Brewery, VpBrewery, RbBrewery)


def get_database():
    return init_db()


def replace_name(name):
    replacements = [
        u'microbrouwerij', 'brewery company', 'old brewery',
        u'bryggeriet', u'bryggeri & spiseri', u'bryggeri', u'brasserie de l’',
        u'brasserie de', u'brewery', u'brygghus', u'bryghus',
        u'brewing co.', 'breweries', 'brewing comp.', 'beer company',
        u'brewing company', u'bieres de ', u'brouwerij', u'brasserie',
        u'trappistenbier-brauerei',  u'pivovary', u'brewing', u'øl', ' as',
        'beer', 'the ', ' co', 'abbaye du'
    ]
    for r in replacements:
        name = name.replace(r, '')
    return name.strip()


def find_brewery(name, breweries):

    name = name.lower()
    for brewery in breweries:
        if brewery.name:
            bname = brewery.name.lower()
            if bname == name:
                return brewery
            if replace_name(name) == replace_name(bname):
                return brewery
    replaced = re.sub(r'\([^)]*\)', '', name)
    if replaced != name:
        return find_brewery(replaced, breweries)
    return None


def map_sources():
    db_session, db_metadata, db_engine = get_database()
    vp_breweries = db_session.query(VpBrewery)\
                             .filter(VpBrewery.brewery_id == None).all()
    for vp_brewery in vp_breweries:
        brewery = Brewery(vp_brewery.name)
        db_session.add(brewery)
        db_session.commit()
        vp_brewery.brewery_id = brewery.id
    db_session.commit()

    breweries = db_session.query(Brewery).all()
    rb_breweries = db_session.query(RbBrewery)\
                             .filter(RbBrewery.brewery_id == None)
    for rb_brewery in rb_breweries:
        brewery = find_brewery(rb_brewery.name, breweries)
        if brewery:
            print 'Mapped: ', brewery.name
            rb_brewery.brewery_id = brewery.id
    db_session.commit()


if __name__ == '__main__':
    map_sources()
