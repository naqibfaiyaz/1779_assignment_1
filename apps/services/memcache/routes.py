# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.services.memcache import blueprint
from flask import render_template, json, request, jsonify, Response, redirect
# from flask_login import login_required

from apps.services.memcache.util import clearCache, getAllCaches, putCache, getSingleCache, invalidateCache, getCurrentPolicy, setCurrentPolicy
from apps.services.memcache.forms import ImageForm
from apps.services.helper import upload_file, getBase64
from apps import memcache, logging, db
from pympler import asizeof
from apps.services.memcache.models import memcahceRequests, knownKeys, policyConfig, memcacheStates
import re

@blueprint.route('/index')
# @login_required
def RedirectIndex():
    return render_template('home/index.html', segment='index')

@blueprint.route('/')
# @login_required
def index():
    return render_template('home/index.html', segment='index')

@blueprint.route('/clearAll')
def clear():
    return render_template("photoUpload/photos.html", msg=json.loads(clearCache())["msg"])

@blueprint.route('/api/delete_all', methods=["POST"])
def test_delete_all():
    try:
        test_getMemcacheSize()
        db.session.query(knownKeys).delete()
        db.session.commit()

        response = clearCache()
    except:
        db.session.rollback()
    
    if 'success' in response and response['success']=='true':
        test_getMemcacheSize()
        return Response(json.dumps(response), status=200, mimetype='application/json')
    else:
        test_getMemcacheSize()
        return Response(json.dumps(response), status=response['error']['code'], mimetype='application/json')

@blueprint.route('/api/list_cache', methods=["POST"])
def test_list_keys_cache():
    test_getMemcacheSize()
    return getAllCaches()

@blueprint.route('/api/list_keys', methods=["POST"])
def test_list_keys_db():
    test_getMemcacheSize()
    allDBKeys=knownKeys.query.all()
    knownKeysInDB={i.key:i.serialize for i in allDBKeys}
    print(type(knownKeysInDB))
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
    test_getMemcacheSize()
    login_form = ImageForm(meta={'csrf': False})
    logging.info(str(login_form))
    if login_form.validate_on_submit():
        requestedKey = request.form.get('key')
        image_path = upload_file(request.files['file'])
        logging.info(requestedKey)
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
        test_getMemcacheSize()
        if 'success' in response and response['success']=='true':
            return Response(json.dumps(response), status=response['code'] if 'code' in response else 200, mimetype='application/json')
        else:
            return Response(json.dumps(response), status=response['error']['code'], mimetype='application/json')

    else:
        return Response(json.dumps({"success": "false", "error": {"code": 400, "message": str(login_form.errors.items())}}), status=400, mimetype='application/json')


@blueprint.route('/api/key/<url_key>', methods=["POST"])
def test_retrieval(url_key):
    test_getMemcacheSize()
    requestedKey = url_key or request.form.get('key')
    response = getSingleCache(requestedKey)

    if "success" in response and response['success']=="true":
        cacheState='hit'
    else:
        cacheState='miss'
        keyFromDB = knownKeys.query.filter_by(key=requestedKey).first()
        if keyFromDB:
            knowKey=keyFromDB.key
            image_path=keyFromDB.img_path
            base64_img=getBase64(image_path)
            response = getSingleCache(requestedKey) if putCache(requestedKey, base64_img)["success"]=="true" else {"data": {"success": True, "key": knowKey, "content": image_path}}
    
    newRequest = memcahceRequests(type = cacheState,
                    known_key = requestedKey)
    db.session.add(newRequest)   
    db.session.commit()
    response['cache_status'] = cacheState
    test_getMemcacheSize()
    if 'success' in response and response['success']=='true':
        return Response(json.dumps(response), status=200, mimetype='application/json')
    else:
        return Response(json.dumps(response), status=404, mimetype='application/json')

@blueprint.route('/api/refreshConfig', methods={"POST"})
def refreshConfiguration():
    test_getMemcacheSize()
    if request.form.get("replacement_policy") and request.form.get("capacity"):
        currentPolicy=policyConfig.query.filter_by(policy_name='replacement_policy').first()
        if currentPolicy:
            currentPolicy.value=request.form.get("replacement_policy")
        else:
            newPolicy = policyConfig(policy_name = "replacement_policy",
                    value = request.form.get("replacement_policy"))
            db.session.add(newPolicy)  
        db.session.commit()

        if request.form.get("replacement_policy")=='no_cache':
            RequestedCapacity = 0
        else: 
            RequestedCapacity =  request.form.get("capacity")
        
        currentcapacity=policyConfig.query.filter_by(policy_name='capacity').first()
        if currentcapacity:
            currentcapacity.value=RequestedCapacity
        else:
            newPolicy = policyConfig(policy_name = "capacity",
                    value = RequestedCapacity)
            db.session.add(newPolicy)  
        
        db.session.commit()
        return Response(json.dumps(setCurrentPolicy(request.form.get("replacement_policy"), RequestedCapacity)), status=200, mimetype='application/json')
        
    else: 
        return Response(json.dumps({
            "success": "false",
            "msg": "Either replacement_policy or capacity or both are missing."
        }), status=400, mimetype='application/json')

@blueprint.route('/api/getMemcacheSize', methods={"GET"})
def test_getMemcacheSize():
    try:
        currentItemNo=memcacheStates(type = 'number_of_items',
            value = len(memcache),
            unit = 'items'
        )

        db.session.add(currentItemNo)  
        db.session.commit()

        currentCacheSize=memcacheStates(type = 'total_cache_size',
            value = asizeof.asizeof(memcache)/1024,
            unit = 'KB'
        )

        db.session.add(currentCacheSize)  
        db.session.commit()

        return Response(json.dumps({
            'success': 'true',
            'data': {
                'number_of_items': currentItemNo.value,
                'total_cache_size': currentCacheSize.value
        }}), status=200, mimetype='application/json')

    except Exception as e:
        logging.error("Error from test_getMemcacheSize: " + str(e))
        Response(json.dumps({
            "success": "false",
            "error": { 
                "code": 500,
                "message": str(e)
                }
            }), status=400, mimetype='application/json')

@blueprint.route('/api/getConfig', methods={"GET"})
def test_getConfig():
    return getCurrentPolicy()



# @blueprint.route('/getCacheSize')
# def getCacheSize():
#     cache = memcache
#     size= asizeof.asizeof(cache)/1024/1024
#     size2= sys.getsizeof(cache)/1024/1024
#     logging.info(size)
#     return {
#         "memcache_size1": size,
#         "memcache_size2": size2,
#         "memcache": len(cache)
#         }

@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
