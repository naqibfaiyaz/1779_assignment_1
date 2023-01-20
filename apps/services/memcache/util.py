# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, request, json, Response
from flask_login import login_required
from apps import memcache,logger
import logging, datetime


# Inspiration -> https://www.vitoshacademy.com/hashing-passwords-in-python/


def getSingleCache(key):
    try:
        if key in memcache:
            jsonCache = memcache[key]
            logger.info({
                key: jsonCache
                })
            response = Response(
                response=json.dumps(jsonCache),
                status=200,
                mimetype='application/json'
            )
        else:
            response = Response(
                response=json.dumps("Unknown key"),
                status=400,
                mimetype='application/json'
            )

        logger.info(response)
        return response
    except Exception as e:
        logging.error("Error from putCache: " + str(e))
        return json.dumps(e)

def putCache(key, value):
    memcache[key] = {
        "img": value,
        "accessed_at": None,
        "created_at": datetime.datetime.now(),
    }

    logger.info(memcache[key])
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
