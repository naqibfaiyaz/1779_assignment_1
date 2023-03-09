# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin

from apps import db

from sqlalchemy import Enum, text, ForeignKey

class knownKeys(db.Model):

    __tablename__ = 'known_keys'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    img_path = db.Column(db.String(250))
    created_at = db.Column(db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = db.Column(db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            setattr(self, property, value)
        
    @property
    def serialize(self):
        return {
                'id': self.id,
                'key': self.key,
                'img_path': self.img_path,
                'created_at': self.created_at,
                'updated_at': self.updated_at
        }

# class memcahceRequests(db.Model):

    # __tablename__ = 'memcache_hit_miss'

    # id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # type = db.Column(Enum('hit','miss'))
    # known_key = db.Column(db.String(64), nullable=True)
    # created_at = db.Column(db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    # updated_at = db.Column(db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    # def __init__(self, **kwargs):
    #     for property, value in kwargs.items():
    #         # depending on whether value is an iterable or not, we must
    #         # unpack it's value (when **kwargs is request.form, some values
    #         # will be a 1-element list)
    #         if hasattr(value, '__iter__') and not isinstance(value, str):
    #             # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
    #             value = value[0]

    #         setattr(self, property, value)

# class memcacheStates(db.Model):

#     __tablename__ = 'memcache_states'

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     type = db.Column(Enum('number_of_items','total_cache_size'))
#     value = db.Column(db.Integer)
#     unit = db.Column(Enum('items','MB', 'KB'))
#     created_at = db.Column(db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
#     updated_at = db.Column(db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

#     def __init__(self, **kwargs):
#         for property, value in kwargs.items():
#             # depending on whether value is an iterable or not, we must
#             # unpack it's value (when **kwargs is request.form, some values
#             # will be a 1-element list)
#             if hasattr(value, '__iter__') and not isinstance(value, str):
#                 # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
#                 value = value[0]

#             setattr(self, property, value)

