# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.services.memcache import blueprint
from flask import render_template, json, request
# from flask_login import login_required
from apps.services.memcache.util import clearCache, getAllCaches, putCache, getSingleCache
from apps.services.photoUpload.util import upload_file, getBase64
from apps import memcache, logging, memcache_config
from pympler import asizeof
# import sys


@blueprint.route('/index')
# @login_required
def index():
    return render_template('home/index.html', segment='index')

@blueprint.route('/clearAll')
def clear():
    return render_template("photoUpload/photos.html", msg=json.loads(clearCache())["msg"])

@blueprint.route('/memcache')
def refreshConfiguration():
    return 

@blueprint.route('/api/delete_all', methods={"POST"})
def test_delete_all():
    #logging.info(clearCache())
    return clearCache()

@blueprint.route('/api/list_keys', methods={"POST"})
def test_list_keys():
    return getAllCaches()

@blueprint.route('/api/upload', methods={"POST"})
def test_upload():
    if request.form.get('key') and request.files['file']:
        key = request.form.get('key')
        image = upload_file(request.files['file'])
        base64_img=getBase64(image)
        
        response = putCache(key, base64_img)
        return response

    else:
        return json.dumps({"Failure: No image given."})

@blueprint.route('/api/key/<url_key>', methods={"POST"})
def test_retrieval(url_key):
    key = url_key or request.form.get('key')
    logging.info(getSingleCache(key))
    return getSingleCache(key)


@blueprint.route('/api/getMemcacheSize', methods={"GET"})
def test_getMemcacheSize():
    return {
        "size": asizeof.asizeof(memcache)
    }

@blueprint.route('/api/getConfig', methods={"GET"})
def test_getConfig():
    return memcache_config

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
