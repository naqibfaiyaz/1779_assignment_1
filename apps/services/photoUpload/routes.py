# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.services.photoUpload import blueprint
from apps.services.memcache.util import getSingleCache, putCache, getAllCaches
from flask import render_template, request, json, Response
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps import memcache
import logging
from apps.services.home.routes import get_segment

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
        logging.error(str(e))
        return render_template('home/page-500.html'), 500


@blueprint.route('/put',methods=['POST', 'PUT'])
def putPhoto():
    key = request.form.get('key')
    value = request.form.get('value')

    response = putCache(key, value)

    logging.info('Put request received- ', key, value)

    if 'savePhoto' in request.form:
        return render_template("photoUpload/addPhoto.html", msg=json.loads(response.data))

    return response

@blueprint.route('/get', defaults={'url_key': None}, methods=['POST'])
@blueprint.route('/get/<url_key>',methods=['GET', 'POST'])
def getSinglePhoto(url_key):
    key = url_key or request.form.get('key')
    logging.info(request.form)
    cacheData = json.loads(getSingleCache(key).data)
    logging.info('Get request received for single key- ' + key, cacheData)
    logging.info(cacheData)
    if url_key:
        return render_template("photoUpload/addPhoto.html", data=cacheData)
    return cacheData

@blueprint.route('/getAll',methods=['POST'])
def getAllPhotos():
    logging.info('Get request received for all keys- ')

    allCacheData = json.loads(getAllCaches().data)

    logging.info(allCacheData)
    return allCacheData
