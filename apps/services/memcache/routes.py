# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.services.memcache import blueprint
from flask import render_template, json, request, jsonify, Response, redirect
# from flask_login import login_required

from apps.services.memcache.util import clearCache, getAllCaches, putCache, getSingleCache, invalidateCache, getCurrentPolicy, setCurrentPolicy
from apps.services.memcache.forms import ImageForm
from apps.services.helper import getBase64
from apps import memcache, logging, db
from pympler import asizeof
from apps.services.memcache.models import knownKeys
# from apps.services.cloudWatch.routes import put_metric_data_cw
import re

@blueprint.route('/index')
# @login_required
def RedirectIndex():
    return index()

@blueprint.route('/')
# @login_required
def index():
    return render_template('home/index.html', segment='index')

@blueprint.route('/api/clearAll', methods=["GET", "POST"])
def clear():
    return clearCache()

@blueprint.route('/api/delete_all', methods=["POST"])
def test_delete_all():
    try:
        # test_getMemcacheSize()
        db.session.query(knownKeys).delete()
        db.session.commit()

        response = clearCache()
    except:
        db.session.rollback()
    
    if 'success' in response and response['success']=='true':
        # test_getMemcacheSize()
        return Response(json.dumps(response), status=200, mimetype='application/json')
    else:
        # test_getMemcacheSize()
        return Response(json.dumps(response), status=response['error']['code'], mimetype='application/json')

@blueprint.route('/api/list_cache', methods=["POST"])
def test_list_keys_cache():
    # test_getMemcacheSize()
    return getAllCaches()

@blueprint.route('/api/list_keys', methods=["POST"])
def test_list_keys_db():
    # test_getMemcacheSize()
    allDBKeys=knownKeys.query.all()
    knownKeysInDB={i.key:i.serialize for i in allDBKeys}
    
    return {
                "content": knownKeysInDB,
                "success": "true",
                "keys": list(knownKeysInDB.keys())
            }

@blueprint.route('/api/invalidate/<url_key>', methods=["GET","POST"])
def test_invalidate(url_key):
    return invalidateCache(url_key)

@blueprint.route('/api/upload', methods=["POST"])
def test_upload():
    # test_getMemcacheSize()
    login_form = ImageForm(meta={'csrf': False})
    logging.info(str(login_form))
    if login_form.validate_on_submit():
        requestedKey = request.form.get('key')
        image_path = request.form.get('image_path')
        logging.info(requestedKey)
        logging.info(image_path)
        key = knownKeys.query.filter_by(key=requestedKey).first()
        
        if key:
            invalidateCache(requestedKey)
            key.img_path=image_path
            db.session.commit()
        else:
            newKeyEntry = knownKeys(key = requestedKey,
                    img_path = image_path)
            db.session.add(newKeyEntry)   
            db.session.commit()

        base64_img=getBase64(image_path)
        
        response = putCache(requestedKey, base64_img)
        # test_getMemcacheSize()
        if 'success' in response and response['success']=='true':
            return Response(json.dumps(response), status=response['code'] if 'code' in response else 200, mimetype='application/json')
        else:
            return Response(json.dumps(response), status=response['error']['code'], mimetype='application/json')

    else:
        return Response(json.dumps({"success": "false", "error": {"code": 400, "message": str(login_form.errors.items())}}), status=400, mimetype='application/json')


@blueprint.route('/api/key/<url_key>', methods=["POST"])
def test_retrieval(url_key):
    # test_getMemcacheSize()
    requestedKey = url_key or request.form.get('key')
    print(requestedKey)
    response = getSingleCache(requestedKey)
    print(response)
    if "success" in response and response['success']=="true":
        cacheResponse='hit'
    else:
        cacheResponse='miss'
        keyFromDB = knownKeys.query.filter_by(key=requestedKey).first()
        if keyFromDB:
            knowKey=keyFromDB.key
            image_path=keyFromDB.img_path
            base64_img=getBase64(image_path)
            newResponse={
                "success": "true", 
                "key": knowKey, 
                "content": {
                    "img": base64_img,
                    "accessed_at": None,
                    "accessed_at_in_millis": None,
                    "created_at": None,
                    "image_size": None,
                    "msg": "Serving from database directly"
                }}
            response = newResponse if "cache" in putCache(requestedKey, base64_img) and putCache(requestedKey, base64_img)['cache']=='miss' else getSingleCache(requestedKey)
    
    # newRequest = memcahceRequests(type = cacheState,
    #                 known_key = requestedKey)
    # db.session.add(newRequest)   
    # db.session.commit()
    response['cache_status'] = cacheResponse
    print(response)
    if 'success' in response and response['success']=='true':
        return Response(json.dumps(response), status=200, mimetype='application/json')
    else:
        return Response(json.dumps(response), status=404, mimetype='application/json')

@blueprint.route('/api/refreshConfig', methods={"POST"})
def refreshConfiguration():
    # test_getMemcacheSize()
    if request.form.get("replacement_policy") and request.form.get("capacity"):
        
        return Response(json.dumps(setCurrentPolicy(request.form.get("replacement_policy"), request.form.get("capacity"))), status=200, mimetype='application/json')
        
    else: 
        return Response(json.dumps({
            "success": "false",
            "msg": "Either replacement_policy or capacity or both are missing."
        }), status=400, mimetype='application/json')

@blueprint.route('/api/getConfig', methods=["GET"])
def test_getConfig():
    return getCurrentPolicy()


@blueprint.route('/api/getCacheData', methods=["POST"])
def getCacheSize():
    cache = memcache
    size= asizeof.asizeof(cache)/1024/1024
    logging.info(size)
    return {
        "memcache_size_mb": size,
        "memcache_keys_count": len(cache)
        }

@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
