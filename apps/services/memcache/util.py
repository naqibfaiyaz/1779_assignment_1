# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from pympler import asizeof
import random
import time
from flask import json
from apps import memcache, logger, memcache_config
import datetime
import pandas as pd


# Inspiration -> https://www.vitoshacademy.com/hashing-passwords-in-python/

def getSingleCache(key):
    """Return json string of requested key and its value. Return "current key is not present in the cache" if key is not found. This test will not be passed as there are time info in the variable.
    >>> memcache["test1"]={"img": "http://127.0.0.1/static/asset/public/img1.jpg","accessed_at": "2023-12-12 16:40","created_at": "2023-12-12 16:40"}
    >>> memcache["test2"]={"img": "http://127.0.0.1/static/asset/public/img1.jpg","accessed_at": "2023-12-12 16:40","created_at": "2023-12-12 16:40"}
    >>> getSingleCache("test1")
    '{"content": {"accessed_at": "Wed, 25 Jan 2023 16:18:06 GMT", "created_at": "2023-12-12 16:40", "img": "http://127.0.0.1/static/asset/public/img1.jpg"}, "key": ["test1"], "success": "true"}'
    >>> invalidateCache('test1')
    '{"data": {}, "msg": "test1 has been invalidated"}'
    >>> getSingleCache("test1")
    '{"error": {"code": 400, "message": "test1 is not present in the cache"}, "success": "false"}'
    """
    try:
        if key in memcache:
            jsonCache = memcache[key]
            jsonCache.update({"accessed_at": datetime.datetime.now()})
            jsonCache.update({"accessed_at_in_millis": round(time.time())})
            response = {
                "success": "true",
                "key": key,
                "content": jsonCache
            }
        else:
            if memcache_config["memcache_policy"]=='no_cache':
                response = {
                    "success": "false",
                    "key": key + " is not present in the cache",
                    "content": "no_cache policy is active"
                }
            else:
                raise ValueError(key + " is not present. Please upload the key and image.")

        logger.info("Response from getSingleCache ")
        logger.info(str(response["success"]))
        return response
    except ValueError as ve:
        logger.error("Error from getSingleCache: " + str(ve))
        return {
            "success": "false",
            "error": { 
                "code": 400,
                "message": str(ve)
                }
            }
    except Exception as e:
        logger.error("Error from getSingleCache: " + str(e))
        return {
            "success": "false",
            "error": { 
                "code": 500,
                "message": str(e)
                }
            }

def putCache(key, value):
    """Return json string of requested key and its value after adding/replacing them in the cache
    >>> putCache("test1", "/static/asset/public/img1.jpg") 
    '{"data": {"test1": "/static/asset/public/img1.jpg"}, "keys": ["test1"], "msg": "test1 : Successfully Saved", "success": "true"}'
    """
    # setCurrentPolicy(policyConfig.query.filter_by(policy_name='policy').first().value, policyConfig.query.filter_by(policy_name='cacheSize').first().value)
    memcache_config["memcache_size"] = asizeof.asizeof(memcache)
    
    logger.info(memcache_config)
    image_size = asizeof.asizeof(value)
    logger.info(image_size)
    logger.info(memcache_config["memcache_capacity"])
    if image_size > memcache_config["memcache_capacity"]:
        logger.warning("putCache: Image Size exceeds memcache capacity.")
        response = {"success": "true","msg": "Image Size exceeds memcache capacity, inserted in table not in memcache", "code": 201, "cache": "miss"
            }
        return response

    memcache_free_space = memcache_config["memcache_capacity"] - memcache_config["memcache_size"]
    if image_size > memcache_free_space:
        try:
            logger.info("putCache: Freeing up Cache.")
            freeCache(image_size - memcache_free_space)

        except Exception as e:
            logger.error("Error from freeCache: " + str(e))
            logger.warning("Could not free up space for putCache.")
            return e

    try:
        memcache[key] = {
            "img": value,
            "accessed_at": datetime.datetime.now(),
            "accessed_at_in_millis": round(time.time()),
            "created_at": datetime.datetime.now(),
            "image_size": image_size
        }

        memcache_config["memcache_size"] += image_size

        response = {
            # "data": {
            #     key: memcache[key]["img"]
            # },
            "success": "true",
            "key": key,
            "msg": key + ' : Successfully Saved'
        }

        logger.info("response from putCache " + str(response["success"]))
        return response
    except Exception as e:
        logger.error("Error from putCache: " + str(e))
        return {
            "success": "false",
            "error": { 
                "code": 500,
                "message": str(e)
                }
            }

def freeCache(space_required):
    memcache_policy = memcache_config["memcache_policy"]
    freed_space = 0

    try:
        if memcache_policy == "LRU":

            df_memcache = pd.DataFrame.from_dict(memcache).T
            df_memcache = df_memcache[["accessed_at_in_millis"]]
            df_memcache = df_memcache.sort_values(by="accessed_at_in_millis", ascending=True).T

            while freed_space < space_required:
                element_to_delete = df_memcache.pop(df_memcache.columns[0]).name
                freed_space_from_single = memcache[element_to_delete]["image_size"]
                invalidateCache(element_to_delete)
                memcache_config["memcache_size"] -= freed_space_from_single
                freed_space += freed_space_from_single
                # index += 1

        elif memcache_policy == "random":
            while freed_space < space_required:
                element_to_delete = random.choice(list(memcache.keys()))
                freed_space_from_single = memcache[element_to_delete]["image_size"]
                invalidateCache(element_to_delete)
                memcache_config["memcache_size"] -= freed_space_from_single
                freed_space += freed_space_from_single

        elif memcache_policy == "no_cache":
            clearCache()
            memcache_config["memcache_size"]=asizeof.asizeof(memcache)

        # else:
        #     logger.error()
        #     raise Exception("No valid memcache policy selected.")

        response = {"success": "true"}
        return response

    except Exception as e:
        logger.error("Error from freeCache: " + str(e))
        return e


def getAllCaches():
    """Return string, after invalidating a cache 
    >>> memcache["test1"]={"img": "http://127.0.0.1/static/asset/public/img1.jpg","accessed_at": "2023-12-12 16:40","created_at": "2023-12-12 16:40"}
    >>> memcache["test2"]={"img": "http://127.0.0.1/static/asset/public/img1.jpg","accessed_at": "2023-12-12 16:40","created_at": "2023-12-12 16:40"}
    >>> getAllCaches()
    '{"content": {"test1": {"accessed_at": "2023-12-12 16:40", "created_at": "2023-12-12 16:40", "img": "http://127.0.0.1/static/asset/public/img1.jpg"}, "test2": {"accessed_at": "2023-12-12 16:40", "created_at": "2023-12-12 16:40", "img": "http://127.0.0.1/static/asset/public/img1.jpg"}}, "keys": ["test1", "test2"], "success": "true"}'
    """

    try:
        cachedData={}
        for key in memcache:
            cachedData[key] = {
                "key": key,
                "created_at": memcache[key]["created_at"],
                "accessed_at": memcache[key]["accessed_at"]
            }
        response = {
                "content": cachedData,
                "success": "true",
                "keys": list(cachedData.keys())
            }

        logger.info("response from getAllCaches " + str(response["success"]))
        return response
    except Exception as e:
        logger.error("Error from getAllCaches: " + str(e))
        return e

def clearCache()->str:
    """Return json string, after clearing cache 

    >>> clearCache()
    '{"data": {}, "success": "true"}'
    """
    try:
        print(memcache)
        memcache.clear()
        response={
                "success": "true",
                "data": memcache
            }
        # logger.info("response from clearCache " + str(response["success"]))
        return response
    except Exception as e:
        logger.error("Error from clearCache: " + str(e))
        return {
            "success": "false",
            "error": { 
                "code": 500,
                "message": str(e)
                }
            }

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

        logger.info("response from invalidateCache: " + str(response["msg"]))
        return response
    except Exception as e:
        logger.error("Error from invalidateCache: " + str(e))
        return e

def getCurrentPolicy():
    return {
        "success": "true",
        "content": memcache_config
    }

def setCurrentPolicy(policy, capacity):
    try:
        memcache_config["memcache_policy"]=policy
        memcache_config["memcache_capacity"]=int(capacity)*1024*1024

        memcache_free_space = memcache_config["memcache_capacity"] - memcache_config["memcache_size"]
        image_size=0
        freeCache(image_size - memcache_free_space)
        return {
            "success": "true",
            "content": memcache_config
        }
    except Exception as e:
        logger.error("Error from clearCache: " + str(e))
        return {
            "success": "false",
            "error": { 
                "code": 500,
                "message": str(e)
                }
            }