# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, request, json, Response
from flask_login import login_required
from apps import memcache
import logging


# Inspiration -> https://www.vitoshacademy.com/hashing-passwords-in-python/


def getSingleCache(key):
    try:
        if key in memcache:
            value = memcache[key]
            response = Response(
                response=json.dumps({
                    key: value,
                }),
                status=200,
                mimetype='application/json'
            )
        else:
            response = Response(
                response=json.dumps("Unknown key"),
                status=400,
                mimetype='application/json'
            )

        return response
    except Exception as e:
        logging.error("Error from putCache: " + str(e))
        return json.dumps(e)

def putCache(key, value):
    memcache[key] = value

    try:
        response = Response(
            response=json.dumps(key + ' : Successfully Saved'),
            status=200,
            mimetype='application/json'
        )

        return response
    except Exception as e:
        logging.error("Error from putCache: " + str(e))
        return json.dumps(e)

def getAllCaches():
    try:
        response = Response(
            response=json.dumps(memcache),
            status=200,
            mimetype='application/json'
        )
        
        return response
    except Exception as e:
        logging.error("Error from putCache: " + str(e))
        return json.dumps(e)
