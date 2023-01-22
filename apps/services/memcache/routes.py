# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.services.memcache import blueprint
from flask import render_template, json
# from flask_login import login_required
from apps.services.memcache.util import clearCache


@blueprint.route('/index')
# @login_required
def index():
    return render_template('home/index.html', segment='index')

@blueprint.route('/clearAll')
def clear():
    return render_template("photoUpload/photos.html", msg=json.loads(clearCache())["msg"])
