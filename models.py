# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import (Column, Integer, String, Numeric, DateTime,
                        ForeignKey)
from sqlalchemy.orm import relationship

from database import Base


class Brewery(Base):
    __tablename__ = 'breweries'
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(255))

    vp_brewery = relationship('VpBrewery', uselist=False, backref='brewery')
    rb_brewery = relationship('RbBrewery', uselist=False, backref='brewery')

    def __init__(self, name):
        self.name = name


class VpBrewery(Base):
    __tablename__ = 'vp_breweries'
    id = Column('id', Integer, primary_key=True)
    beers = relationship('VpBeer', backref='brewery')
    name = Column('name', String(255))
    brewery_id = Column(Integer, ForeignKey('breweries.id'))

    def __init__(self, name):
        self.name = name


class VpBeer(Base):
    __tablename__ = 'vp_beers'
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(255))
    pol_url = Column('pol_url', String(255))
    country = Column('country', String(100))
    pol_price = Column('pol_price', Numeric)
    pol_type = Column('pol_type', String(20))
    pol_cat = Column('pol_cat', String(20))
    abv = Column('abv', Numeric)
    availability = Column('availability', String(50))
    main_type = Column('main_type', String(50))
    pol_id = Column('pol_id', Integer)
    pol_size = Column('pol_size', Numeric)
    brewery_id = Column(Integer, ForeignKey('vp_breweries.id'))
    added = Column('added', DateTime, default=datetime.now)
    updated = Column('updated', DateTime)

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', None)
        self.pol_url = kwargs.get('url', None)
        country = kwargs.get('country', None)
        if country:
            country = country.split(',')[0]
        self.country = country
        self.abv = kwargs.get('abv', None)
        self.pol_id = kwargs.get('id', None)
        self.pol_size = kwargs.get('size', None)
        self.main_type = kwargs.get('type', None)

        self.pol_price = kwargs.get('price', None)
        self.pol_type = kwargs.get('pol_type', None)
        self.pol_cat = kwargs.get('pol_cat', None)
        self.availability = kwargs.get('stock', None)


class RbBrewery(Base):
    __tablename__ = 'rb_breweries'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    brewery_id = Column(Integer, ForeignKey('breweries.id'))

    def __init__(self, name):
        assert(name is not None)
        assert(name != "")
        self.name = name


class RbBeer(Base):
    __tablename__ = 'rb_beers'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    ratebeer_id = Column(Integer)
    short_name = Column(String(255), nullable=False)
    brewery_id = Column(Integer, ForeignKey("rb_breweries.id"), nullable=False)
    brewery = relationship("RbBrewery", lazy=False)
    rating = Column(Numeric, nullable=False)
    num = Column(Numeric, nullable=True)

    def __init__(self, ratebeer_id, name, short_name, brewery, rating, num):
        assert(brewery is not None)
        self.ratebeer_id = ratebeer_id
        self.name = name
        self.short_name = short_name
        self.brewery = brewery
        self.rating = rating
        self.num = num
