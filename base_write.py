# -*- coding: utf-8 -*-

from sqlalchemy.orm.exc import NoResultFound

from database import init_db
from models import (VpBeer, VpBrewery, RbBeer, RbBrewery)


def get_database():
    return init_db()


def save_vp_beer(beer_data, db_session):
    try:
        beer = db_session.query(VpBeer).filter(
            VpBeer.pol_id == beer_data['id']
        ).one()
        beer.update(**beer_data)
    except NoResultFound:
        brewery_name = beer_data['brewery']
        try:
            brewery = db_session.query(VpBrewery).filter(
                VpBrewery.name == brewery_name
            ).one()
        except NoResultFound:
            brewery = VpBrewery(brewery_name)
            db_session.add(brewery)
            db_session.commit()
        beer = VpBeer(**beer_data)
        beer.brewery = brewery

    db_session.add(beer)


def write_vp_data(beers):
    db_session, db_metadata, db_engine = get_database()
    for beer in beers:
        save_vp_beer(beer, db_session)
    db_session.commit()


def get_rb_brewery(name, db_session):
    try:
        return db_session.query(RbBrewery).filter(RbBrewery.name == name).one()
    except NoResultFound:
        brewery = RbBrewery(name)
        db_session.add(brewery)
        db_session.commit()
        db_session.refresh(brewery)
        return brewery


def create_or_update_rb_beer(db_session, ratebeer_id, name,
                             short_name, brewery, rating, num):
    try:
        beer = db_session.query(RbBeer).filter(RbBeer.name == name).one()
        beer.rating = rating
        beer.num = num
    except NoResultFound:
        beer = RbBeer(ratebeer_id, name, short_name, brewery, rating, num)
    db_session.add(beer)


def write_rb_data(breweries):
    db_session, db_metadata, db_engine = get_database()
    for brewery_name in breweries.keys():
        brewery = RbBrewery(brewery_name)
        db_session.add(brewery)
    db_session.commit()

    counter = 0
    for brewery_name, beers in breweries.items():
        brewery = get_rb_brewery(brewery_name, db_session)
        for beer in beers:
            create_or_update_rb_beer(
                db_session,
                beer["id"],
                beer["name"],
                beer["short_name"],
                brewery,
                beer["num1"],
                beer["num2"]
            )
            counter += 1
            if counter % 1000 == 0:
                print counter
    db_session.commit()
