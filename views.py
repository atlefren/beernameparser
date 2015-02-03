# -*- coding: utf-8 -*-

from flask import (render_template, current_app)
from sqlalchemy import and_, or_

from models import (VpBrewery, RbBrewery, Brewery)


def create_views(app):

    @app.route('/')
    def index():
        db = current_app.db_session
        vp_breweries = db.query(VpBrewery).all()
        rb_breweries = db.query(RbBrewery).all()

        breweries = db.query(Brewery)\
                      .filter(and_(
                          Brewery.rb_brewery != None,
                          Brewery.vp_brewery != None,
                      )).all()

        notmapped = db.query(Brewery)\
                      .filter(or_(
                          Brewery.rb_brewery == None,
                          Brewery.vp_brewery == None,
                      ))

        return render_template(
            'index.html',
            rb_breweries=rb_breweries,
            vp_breweries=vp_breweries,
            breweries=breweries,
            notmapped=notmapped,
        )
