import os
from flask import Flask, render_template, request, url_for, redirect
from sqlalchemy.sql import func
from apps import db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://root:root@localhost:3306/appseed_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)

class key_img(db.Model):

    __tablename__ = 'key_img'

    id = db.Column(db.String(64), primary_key=True)
    img_path = db.Column(db.String(200))
    updated_at = db.Column(db.DateTime,default=datetime.now())
    
    def __repr__(self):
        return str(self.id)
    
class memcache_hit_miss(db.Model):

    __tablename__ = 'memcache_hit_miss'

    id = db.Column(db.String(64), primary_key=True)
    type = db.Column(db.String(200))
    requested_img = db.Column(db.String(64))
    
    def __repr__(self):
        return str(self.id)
    
class memcache_states(db.Model):

    __tablename__ = 'memcache_states'

    id = db.Column(db.String(64), primary_key=True)
    img_path = db.Column(db.String(200))
    updated_at = db.Column(db.DateTime,default=datetime.now())
    
    def __repr__(self):
        return str(self.id)
    
class policy_config(db.Model):

    __tablename__ = 'policy_config'

    id = db.Column(db.String(64), primary_key=True)
    policy_id = db.Column(db.String(200))
    policy_value = db.Column(db.DateTime,default=datetime.now())
    value_type=db.Column(db.String(2))
    updated_at=db.Column(db.DateTime,default=datetime.now())
    
    def __repr__(self):
        return str(self.id)

    
class policy_name(db.Model):

    __tablename__ = 'policy_name'

    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(200))
    updated_at=db.Column(db.DateTime,default=datetime.now())
    
    def __repr__(self):
        return str(self.id)
    


    
