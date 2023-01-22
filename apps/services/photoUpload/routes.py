# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.services.photoUpload import blueprint
from apps.services.memcache.util import getSingleCache, putCache, getAllCaches, invalidateCache
from flask import render_template, request, json, redirect, url_for
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps import logger
from apps.services.home.routes import get_segment
from apps.services.photoUpload.util import upload_file

@blueprint.route('/index')
# @login_required
def index():

    return render_template('home/index.html', segment='index')


@blueprint.route('/<template>')
# @login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        if segment=='photos.html':
            return render_template("photoUpload/photos.html", memcache=getAllPhotos())
        return render_template("photoUpload/" + template, segment=segment.replace('.html', ''))

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except Exception as e:
        logger.error(str(e))
        return render_template('home/page-500.html'), 500


@blueprint.route('/put',methods=['POST', 'PUT'])
def putPhoto():
    # UPLOAD_FOLDER = apps.app_c'/static/assets/public/'
    # ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
    if request.form.get('key') and request.files['image']:
        key = request.form.get('key')
        image = upload_file(request.files['image'])
        logger.info(image)

        response = putCache(key, image)

        logger.info('Put request received- ' + key)

        if 'savePhoto' in request.form:
            return render_template("photoUpload/photos.html", msg=json.loads(response)["msg"], memcache=getAllPhotos())
        else:
            return response
    else:
        key = request.form.get('key')
        cacheData = json.loads(getSingleCache(key))
        if key in cacheData:
            return render_template("photoUpload/addPhoto.html", msg="Key exists, please upload a new image", data=cacheData[key], key=key)
        elif key not in cacheData and "msg" in cacheData:
            return render_template("photoUpload/addPhoto.html", msg="Key/Image mismatch, please upload properly")

    

@blueprint.route('/get', defaults={'url_key': None}, methods=['POST'])
@blueprint.route('/get/<url_key>',methods=['GET', 'POST'])
def getSinglePhoto(url_key):
    key = url_key or request.form.get('key')
    logger.info(request.form)
    cacheData = json.loads(getSingleCache(key))
    logger.info('Get request received for single key- ' + key, cacheData)
    logger.info(cacheData)
    if url_key and key in cacheData:
        return render_template("photoUpload/addPhoto.html", data=cacheData[key], key=key)
    elif url_key and key not in cacheData and "msg" in cacheData:
        return render_template("photoUpload/addPhoto.html", msg=cacheData["msg"], key=key)

    return cacheData

@blueprint.route('/getAll',methods=['POST'])
def getAllPhotos():
    logger.info('Get request received for all keys- ')

    allCacheData = json.loads(getAllCaches())

    logger.info(allCacheData)
    return allCacheData

@blueprint.route('/invalivate_key', defaults={'url_key': None}, methods=['POST'])
@blueprint.route('/invalivate_key/<url_key>',methods=['GET', 'POST'])
def invalidateKey(url_key) :
    key = url_key or request.form.get('key')
    response = json.loads(invalidateCache(key))["msg"]
    
    if url_key:
        return redirect(url_for("photoUpload_blueprint.route_template", template="photos.html"))
    return response
