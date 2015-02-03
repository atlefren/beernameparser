# -*- coding: utf-8 -*-

import os

from flask import Flask

from database import init_db
from views import create_views


def create_app(debug):
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'development_fallback')
    app.debug = debug
    (app.db_session, app.db_metadata, app.db_engine) = init_db()

    create_views(app)

    return app


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app = create_app(os.environ.get('DEBUG', False))
    app.run(host='0.0.0.0', port=port, debug=True)

