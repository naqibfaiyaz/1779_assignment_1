# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module
import logging, doctest

global memcache
memcache={}
global memcache_config
memcache_config = {
    "memcache_policy": "LRU",
    "memcache_capacity": 1000000,
    "memcache_size": 0
}
logging.info("Memcache Initialized: ", memcache)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
db = SQLAlchemy()
AWS_ACCESS_KEY=os.getenv('aws_access_key_id')
AWS_SECRET_KEY=os.getenv('aws_secret_access_key')
# login_manager = LoginManager()

def register_extensions(app):
    db.init_app(app)
    # login_manager.init_app(app)


def register_blueprints(app):
    for module_name in ('home', 'memcache'):
        module = import_module('apps.services.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def configure_database(app):

    @app.before_first_request
    def initialize_database():
        try:
            db.create_all()
        except Exception as e:

            print('> Error: DBMS Exception: ' + str(e) )

            # fallback to SQLite
            basedir = os.path.abspath(os.path.dirname(__file__))
            app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')

            print('> Fallback to SQLite ')
            db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove() 


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    logger.info(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    return app
