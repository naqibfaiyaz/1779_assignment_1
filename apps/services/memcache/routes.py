# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.services.memcache import blueprint
from flask import render_template, json, request, jsonify
# from flask_login import login_required

from apps.services.memcache.util import clearCache, getAllCaches, putCache, getSingleCache, invalidateCache, getCurrentPolicy, setCurrentPolicy
from apps.services.memcache.forms import ImageForm
from apps.services.helper import upload_file, getBase64
from apps import memcache, logging, db
from pympler import asizeof
from apps.services.memcache.models import memcahceRequests, knownKeys, policyConfig
import re

@blueprint.route('/index')
# @login_required
def index():
    return render_template('home/index.html', segment='index')

@blueprint.route('/clearAll')
def clear():
    return render_template("photoUpload/photos.html", msg=json.loads(clearCache())["msg"])

@blueprint.route('/api/delete_all', methods=["POST"])
def test_delete_all():
    try:
        db.session.query(knownKeys).delete()
        db.session.commit()

        response = clearCache()
    except:
        db.session.rollback()
    return response

@blueprint.route('/api/list_cache', methods=["POST"])
def test_list_keys_cache():
    return getAllCaches()

@blueprint.route('/api/list_keys', methods=["POST"])
def test_list_keys_db():
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
        return response

    else:
        return json.dumps({"success": False, "error": {"code": 400, "message": str(login_form.errors.items())}})

@blueprint.route('/api/key/<url_key>', methods=["POST"])
def test_retrieval(url_key):
    requestedKey = url_key or request.form.get('key')
    response = getSingleCache(requestedKey)

    if "success" in response and response['success']=="true":
        cacheState='hit'
    else:
        cacheState='miss'
        keyFromDB = knownKeys.query.filter_by(key=requestedKey).first()
        if keyFromDB:
            image_path=keyFromDB.img_path
            base64_img=getBase64(image_path)
            response = getSingleCache(requestedKey) if putCache(requestedKey, base64_img)["success"]=="true" else {"data": {"success": True, "key": knowKey, "content": image_path}}
    
    newRequest = memcahceRequests(type = cacheState,
                    known_key = requestedKey)
    db.session.add(newRequest)   
    db.session.commit()
    response['cache_status'] = cacheState
    return response

@blueprint.route('/api/refreshConfig', methods={"POST"})
def refreshConfiguration():
    if request.form.get("replacement_policy") and request.form.get("capacity"):
        currentPolicy=policyConfig.query.filter_by(policy_name='replacement_policy').first()
        currentPolicy.value=request.form.get("replacement_policy")
        db.session.commit()

        currentcapacity=policyConfig.query.filter_by(policy_name='capacity').first()
        currentcapacity.value=request.form.get("capacity")
        db.session.commit()
        return setCurrentPolicy(request.form.get("replacement_policy"), request.form.get("capacity"))
    else: 
        return {
            "success": False,
            "msg": "Either replacement_policy or capacity or both are missing."
        }

@blueprint.route('/api/getMemcacheSize', methods={"GET"})
def test_getMemcacheSize():
    return {
        "size": asizeof.asizeof(memcache)
    }

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
