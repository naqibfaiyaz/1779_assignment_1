# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import json
from apps import memcache,logger
import datetime


# Inspiration -> https://www.vitoshacademy.com/hashing-passwords-in-python/

def getSingleCache(key):
    """Return json string of requested key and its value. Return "current key is not present in the cache" if key is not found.
    >>> memcache["test1"]={"img": "http://127.0.0.1/static/asset/public/img1.jpg","accessed_at": "2023-12-12 16:40","created_at": "2023-12-12 16:40"}
    >>> memcache["test2"]={"img": "http://127.0.0.1/static/asset/public/img1.jpg","accessed_at": "2023-12-12 16:40","created_at": "2023-12-12 16:40"}
    >>> getSingleCache("test1")
    '{"content": {"accessed_at": "Wed, 25 Jan 2023 16:18:06 GMT", "created_at": "2023-12-12 16:40", "img": "http://127.0.0.1/static/asset/public/img1.jpg"}, "keys": ["test1"], "success": "true"}'
    >>> invalidateCache('test1')
    '{"data": {}, "msg": "test1 has been invalidated"}'
    >>> getSingleCache("test1")
    '{"error": {"code": 400, "message": "test1 is not present in the cache"}, "success": "false"}'
    """
    try:
        if key in memcache:
            jsonCache = memcache[key]
            jsonCache.update({"accessed_at": datetime.datetime.now()})
            response = {
                "success": "true",
                "keys": [key],
                "content": jsonCache
            }
        else:
            raise ValueError(key + " is not present in the cache")

        logger.info("Response from getSingleCache ", str(response))
        return json.dumps(response)
    except ValueError as ve:
        logger.error("Error from getSingleCache: " + str(ve))
        return json.dumps({
            "success": "false",
            "error": { 
                "code": 400,
                "message": str(ve)
                }
            })
    except Exception as e:
        logger.error("Error from getSingleCache: " + str(e))
        return json.dumps({
            "success": "false",
            "error": { 
                "code": 500,
                "message": str(e)
                }
            })

def putCache(key, value):
    """Return json string of requested key and its value after adding/replacing them in the cache
    >>> putCache("test1", "/static/asset/public/img1.jpg") 
    '{"data": {"test1": "/static/asset/public/img1.jpg"}, "keys": ["test1"], "msg": "test1 : Successfully Saved", "success": "true"}'
    """
    try:
        memcache[key] = {
            "img": value,
            "accessed_at": None,
            "created_at": datetime.datetime.now(),
        }

        response = {
            "data": {
                key: memcache[key]["img"]
            },
            "success": "true",
            "keys": [key],
            "msg": key + ' : Successfully Saved'
        }

        logger.info("response from putCache " + str(response))
        return json.dumps(response)
    except Exception as e:
        logger.error("Error from putCache: " + str(e))
        return json.dumps(e)

def getAllCaches():
    """Return string, after invalidating a cache 
    >>> memcache["test1"]={"img": "http://127.0.0.1/static/asset/public/img1.jpg","accessed_at": "2023-12-12 16:40","created_at": "2023-12-12 16:40"}
    >>> memcache["test2"]={"img": "http://127.0.0.1/static/asset/public/img1.jpg","accessed_at": "2023-12-12 16:40","created_at": "2023-12-12 16:40"}
    >>> getAllCaches()
    '{"content": {"test1": {"accessed_at": "2023-12-12 16:40", "created_at": "2023-12-12 16:40", "img": "http://127.0.0.1/static/asset/public/img1.jpg"}, "test2": {"accessed_at": "2023-12-12 16:40", "created_at": "2023-12-12 16:40", "img": "http://127.0.0.1/static/asset/public/img1.jpg"}}, "keys": ["test1", "test2"], "success": "true"}'
    """

    try:
        cachedData = memcache
        response = json.dumps({
                "content": cachedData ,
                "success": "true",
                "keys": list(cachedData.keys())
            })

        logger.info("response from getAllCaches " + str(response))
        return response
    except Exception as e:
        logger.error("Error from getAllCaches: " + str(e))
        return json.dumps(e)

def clearCache()->str:
    """Return json string, after clearing cache 

    >>> clearCache()
    '{"data": {}, "success": "true"}'
    """
    try:
        memcache.clear()
        response={
                "success": "true",
                "data": memcache
            }
        logger.info("response from clearCache " + str(response))
        return json.dumps(response)
    except Exception as e:
        logger.error("Error from clearCache: " + str(e))
        return json.dumps({
            "success": "false",
            "error": { 
                "code": 500,
                "message": str(e)
                }
            })

def invalidateCache(key: str)->str:
    """Return json string, after invalidating a cache 
    >>> memcache["test1"]={"img": "http://127.0.0.1/static/asset/public/img1.jpg","accessed_at": "2023-12-12 16:40","created_at": "2023-12-12 16:40"}
    >>> invalidateCache('test1')
    '{"data": {}, "msg": "test1 has been invalidated"}'
    >>> invalidateCache('test1')
    '{"data": {}, "msg": "test1 is not present in the cache"}'
    """

    try:
        if key in memcache:
            del memcache[key]
            response={
                "data": memcache[key] if key in memcache else {},
                "msg": key + " has been invalidated",
            }
        else:
            response={
                "data": memcache[key] if key in memcache else {},
                "msg": key + " is not present in the cache",
            }

        logger.info("response from invalidateCache: " + str(response))
        return json.dumps(response)
    except Exception as e:
        logger.error("Error from invalidateCache: " + str(e))
        return json.dumps(e)
